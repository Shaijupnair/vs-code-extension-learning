"""
Main Ingestion Pipeline for Java Code RAG System.
Implements two-pass indexing: hierarchy scan + context-aware ingestion.
Configuration is loaded from config.ini file.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
import logging
from datetime import datetime
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parser.hierarchy_scanner import build_project_map
from parser.java_parser import JavaCodeParser
from embedding.enricher import CodeEnricher
from database.vector_store import VectorStore


# Configure logging from config
log_file = config.get('Logging', 'ingestion_log', fallback='ingestion.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Two-pass ingestion pipeline for Java codebase.
    Pass 1: Build hierarchy map
    Pass 2: Parse, enrich, and index with full context
    """
    
    def __init__(
        self,
        root_path: str,
        batch_size: int = 20,
        db_path: str = "./data/lancedb",
        mock_enrichment: bool = False
    ):
        """
        Initialize ingestion pipeline.
        
        Args:
            root_path: Root directory of Java project
            batch_size: Number of chunks per batch
            db_path: Path to vector database
            mock_enrichment: Use mock enrichment (no API calls)
        """
        self.root_path = Path(root_path)
        self.batch_size = batch_size
        self.db_path = db_path
        self.mock_enrichment = mock_enrichment
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'chunks_indexed': 0,
            'total_files': 0
        }
        
        # Error log from config
        error_log_file = config.get('Logging', 'error_log', fallback='ingestion_errors.log')
        self.error_log_path = Path(error_log_file)
        
        # Components (initialized later)
        self.parser = None
        self.enricher = None
        self.vector_store = None
    
    def phase1_hierarchy_scan(self) -> Path:
        """
        Phase 1: Scan codebase and build hierarchy map.
        
        Returns:
            Path to generated hierarchy JSON file
        """
        logger.info("=" * 80)
        logger.info("PHASE 1: Hierarchy Scan (Pass 1)")
        logger.info("=" * 80)
        
        hierarchy_file = self.root_path / "project_hierarchy.json"
        
        logger.info(f"Scanning project: {self.root_path}")
        logger.info(f"Output file: {hierarchy_file}")
        
        # Build hierarchy map
        hierarchy_map = build_project_map(
            str(self.root_path),
            str(hierarchy_file)
        )
        
        logger.info(f"✓ Phase 1 Complete: Hierarchy map built with {len(hierarchy_map)} classes")
        
        return hierarchy_file
    
    def initialize_components(self, hierarchy_file: Path):
        """
        Initialize parser, enricher, and vector store.
        
        Args:
            hierarchy_file: Path to hierarchy JSON
        """
        logger.info("\nInitializing components...")
        
        # Initialize parser with hierarchy context
        self.parser = JavaCodeParser(hierarchy_map_path=str(hierarchy_file))
        logger.info("✓ Parser initialized with hierarchy map")
        
        # Initialize enricher
        self.enricher = CodeEnricher(mock_mode=self.mock_enrichment)
        logger.info(f"✓ Enricher initialized (mock_mode={self.mock_enrichment})")
        
        # Initialize vector store
        self.vector_store = VectorStore(db_path=self.db_path)
        logger.info(f"✓ Vector store initialized at {self.db_path}")
    
    def find_java_files(self) -> List[Path]:
        """
        Recursively find all .java files in project.
        
        Returns:
            List of Java file paths
        """
        logger.info(f"\nScanning for Java files in: {self.root_path}")
        java_files = list(self.root_path.rglob("*.java"))
        logger.info(f"Found {len(java_files)} Java files")
        return java_files
    
    def log_error(self, file_path: Path, error: Exception):
        """
        Log file processing error.
        
        Args:
            file_path: Path to failed file
            error: Exception that occurred
        """
        timestamp = datetime.now().isoformat()
        error_msg = f"[{timestamp}] {file_path}: {type(error).__name__}: {str(error)}\n"
        
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        
        logger.error(f"Error processing {file_path.name}: {error}")
    
    async def phase2_ingestion_loop(self, java_files: List[Path]):
        """
        Phase 2: Parse, enrich, and index all files.
        Uses Single Writer Pattern: parallel processing, sequential DB writes.
        
        Args:
            java_files: List of Java files to process
        """
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: Ingestion Loop (Pass 2) - Single Writer Pattern")
        logger.info("=" * 80)
        
        buffer = []
        all_enriched_chunks = []  # Collect all enriched chunks
        self.stats['total_files'] = len(java_files)
        
        # Process files with progress bar
        with tqdm(total=len(java_files), desc="Processing files", unit="file") as pbar:
            for file_path in java_files:
                try:
                    # Parse file
                    chunks = self.parser.parse_file(str(file_path))
                    
                    # Add file path to chunks
                    for chunk in chunks:
                        chunk['file_path'] = str(file_path)
                    
                    # Add to buffer
                    buffer.extend(chunks)
                    
                    self.stats['files_processed'] += 1
                    
                    # Flush buffer if full - but DON'T write to DB yet
                    if len(buffer) >= self.batch_size:
                        enriched = await self.flush_buffer(buffer)
                        all_enriched_chunks.extend(enriched)  # Collect
                        buffer = []
                        
                        # SINGLE WRITER: Write collected chunks sequentially
                        if len(all_enriched_chunks) >= self.batch_size * 5:  # Write every 100 chunks
                            self._write_to_db_sequential(all_enriched_chunks)
                            all_enriched_chunks = []
                
                except Exception as e:
                    # Log error and continue
                    self.log_error(file_path, e)
                    self.stats['files_failed'] += 1
                
                pbar.update(1)
        
        # Flush remaining buffer
        if buffer:
            enriched = await self.flush_buffer(buffer)
            all_enriched_chunks.extend(enriched)
        
        # SINGLE WRITER: Final write of all remaining chunks
        if all_enriched_chunks:
            self._write_to_db_sequential(all_enriched_chunks)
        
        logger.info("\n✓ Phase 2 Complete: All files processed")
    
    async def flush_buffer(self, buffer: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process buffer: enrich chunks and return them.
        Does NOT write to database - that's done by caller sequentially.
        
        Args:
            buffer: List of parsed chunks
            
        Returns:
            List of enriched chunks ready for database
        """
        if not buffer:
            return []
        
        try:
            # Step A: Enrich chunks (parallel processing OK here)
            enriched_chunks = await self.enricher.enrich_batch(buffer)
            
            logger.debug(f"Enriched {len(enriched_chunks)} chunks")
            return enriched_chunks
        
        except Exception as e:
            logger.error(f"Error enriching buffer: {e}")
            # Log each file in buffer
            for chunk in buffer:
                file_path = chunk.get('file_path', 'unknown')
                self.log_error(Path(file_path), e)
            return []  # Return empty on error
    
    def _write_to_db_sequential(self, enriched_chunks: List[Dict[str, Any]]):
        """
        SINGLE WRITER: Write enriched chunks to database sequentially.
        This method is called from main thread only - no concurrent writes.
        
        Args:
            enriched_chunks: List of enriched chunks to write
        """
        if not enriched_chunks:
            return
        
        try:
            logger.info(f"Writing {len(enriched_chunks)} chunks to database (sequential write)...")
            self.vector_store.add_batch(enriched_chunks)
            self.stats['chunks_indexed'] += len(enriched_chunks)
            logger.info(f"✓ Successfully wrote {len(enriched_chunks)} chunks")
        
        except Exception as e:
            logger.error(f"Error writing to database: {e}")
            # Don't crash - log and continue
            for chunk in enriched_chunks:
                file_path = chunk.get('file_path', 'unknown')
                self.log_error(Path(file_path), e)
    
    async def run(self):
        """
        Execute the complete two-pass ingestion pipeline.
        """
        start_time = datetime.now()
        
        logger.info("\n" + "=" * 80)
        logger.info("Java Code RAG Ingestion Pipeline")
        logger.info("=" * 80)
        logger.info(f"Start time: {start_time}")
        logger.info(f"Project root: {self.root_path}")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Mock enrichment: {self.mock_enrichment}")
        
        # Phase 1: Hierarchy Scan
        hierarchy_file = self.phase1_hierarchy_scan()
        
        # Initialize components
        self.initialize_components(hierarchy_file)
        
        # Find all Java files
        java_files = self.find_java_files()
        
        # Phase 2: Ingestion Loop
        await self.phase2_ingestion_loop(java_files)
        
        # Print final report
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "=" * 80)
        logger.info("Ingestion Complete!")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration}")
        logger.info(f"Total Files Scanned: {self.stats['total_files']}")
        logger.info(f"Files Processed Successfully: {self.stats['files_processed']}")
        logger.info(f"Files Failed: {self.stats['files_failed']}")
        logger.info(f"Chunks Indexed: {self.stats['chunks_indexed']}")
        
        # Database stats
        db_stats = self.vector_store.get_stats()
        logger.info(f"Database Records: {db_stats['count']}")
        
        if self.stats['files_failed'] > 0:
            logger.info(f"\n⚠️  See {self.error_log_path} for error details")
        
        logger.info("=" * 80)


async def main():
    """Main entry point - reads configuration from config.ini."""
    
    # Read configuration from config.ini
    PROJECT_ROOT = config.get('Paths', 'project_root')
    BATCH_SIZE = config.getint('Ingestion', 'batch_size', fallback=20)
    DB_PATH = config.get('Paths', 'database_path', fallback='./data/lancedb')
    MOCK_ENRICHMENT = config.getboolean('Ingestion', 'mock_enrichment', fallback=False)
    
    # Validate project root exists
    if not Path(PROJECT_ROOT).exists():
        logger.error(f"Project root does not exist: {PROJECT_ROOT}")
        logger.error("Please update 'project_root' in config.ini")
        return
    
    # Create pipeline
    pipeline = IngestionPipeline(
        root_path=PROJECT_ROOT,
        batch_size=BATCH_SIZE,
        db_path=DB_PATH,
        mock_enrichment=MOCK_ENRICHMENT
    )
    
    # Run pipeline
    await pipeline.run()


if __name__ == "__main__":
    asyncio.run(main())
