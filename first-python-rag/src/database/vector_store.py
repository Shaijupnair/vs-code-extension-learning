"""
Vector Store using LanceDB and Jina V3 embeddings.
Handles complex structural data: packages, inheritance, overloading.
"""

import json
import hashlib
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
import lancedb
from lancedb.pydantic import LanceModel, Vector
from pydantic import Field
from transformers import AutoModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeChunkSchema(LanceModel):
    """
    Smart schema for code chunks with structural metadata.
    Handles packages, inheritance, and method overloading.
    """
    # Unique ID - hash of (package + class + signature)
    id: str = Field(..., description="Deterministic hash ID")
    
    # Embedding vector (Jina V3 dimension: 1024)
    vector: Vector(1024) = Field(..., description="Jina V3 embedding vector")
    
    # Raw code for display
    code: str = Field(..., description="Raw method body")
    
    # Virtual document for search (summary + keywords + signature + context)
    search_text: str = Field(..., description="Searchable text content")
    
    # Serialized JSON metadata
    metadata: str = Field(..., description="JSON with package, signature, dependencies, inheritance, file_path")


class VectorStore:
    """
    Vector database for code search using LanceDB and Jina V3.
    """
    
    def __init__(
        self,
        db_path: str = "./data/lancedb",
        model_path: str = r"C:\models\huggingface\JinaV3\jina-embeddings-v3",
        table_name: str = "code_chunks",
        use_gpu: bool = True
    ):
        """
        Initialize vector store with Jina V3 model.
        
        Args:
            db_path: Path to LanceDB database
            model_path: Path to local Jina V3 model
            table_name: Name of the table
            use_gpu: Whether to use GPU if available
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        
        # Ensure db directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load Jina V3 model
        logger.info(f"Loading Jina V3 model from {model_path}")
        self.device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        
        self.model = AutoModel.from_pretrained(
            model_path,
            trust_remote_code=True  # Required for Jina V3
        )
        self.model.to(self.device)
        self.model.eval()  # Set to inference mode
        
        logger.info(f"Model loaded on device: {self.device}")
        
        # Connect to LanceDB
        self.db = lancedb.connect(str(self.db_path))
        logger.info(f"Connected to LanceDB at {self.db_path}")
        
        # Table will be created on first add
        self.table = None
    
    def generate_id(self, package: str, class_name: str, signature: str) -> str:
        """
        Generate deterministic ID from package + class + signature.
        Ensures uniqueness for overloaded methods and same-named classes.
        
        Args:
            package: Package name (e.g., "com.example")
            class_name: Class name (e.g., "Calculator")
            signature: Full method signature
            
        Returns:
            64-character hex string (SHA256 hash)
        """
        # Combine all identifying information
        unique_string = f"{package}::{class_name}::{signature}"
        
        # Generate hash
        hash_object = hashlib.sha256(unique_string.encode('utf-8'))
        return hash_object.hexdigest()
    
    def embed_texts(self, texts: List[str], task: str = "retrieval.passage") -> List[List[float]]:
        """
        Generate embeddings using Jina V3 with task-specific API.
        
        Args:
            texts: List of texts to embed
            task: Task type for Jina V3 (default: "retrieval.passage")
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Embedding {len(texts)} texts with task={task}")
        
        with torch.no_grad():
            # Jina V3 specific API with task parameter
            embeddings = self.model.encode(
                texts,
                task=task,
                # Move to same device as model
                device=self.device
            )
        
        # Convert to list of lists
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.cpu().numpy()
        
        return embeddings.tolist()
    
    def build_search_text(self, chunk: Dict[str, Any]) -> str:
        """
        Build the virtual document for search.
        Combines summary, keywords, signature, and context.
        
        Args:
            chunk: Enriched code chunk
            
        Returns:
            Search text string
        """
        parts = []
        
        # Summary
        if 'summary' in chunk and chunk['summary']:
            parts.append(f"Summary: {chunk['summary']}")
        
        # Keywords
        if 'keywords' in chunk and chunk['keywords']:
            keywords_str = ", ".join(chunk['keywords'])
            parts.append(f"Keywords: {keywords_str}")
        
        # Signature
        if 'method_signature' in chunk:
            parts.append(f"Signature: {chunk['method_signature']}")
        
        # Class context
        if 'class_context' in chunk:
            parts.append(f"Context: {chunk['class_context']}")
        
        return " | ".join(parts)
    
    def extract_metadata(self, chunk: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract and structure metadata from chunk.
        
        Args:
            chunk: Code chunk dictionary
            file_path: Path to source file
            
        Returns:
            Metadata dictionary
        """
        # Extract package from class_context
        package = "Unknown"
        class_name = "Unknown"
        inherited_methods = []
        
        class_context = chunk.get('class_context', '')
        
        # Parse package
        if 'Package: ' in class_context:
            package_part = class_context.split(',')[0]
            package = package_part.replace('Package: ', '').strip()
        
        # Parse class name
        if 'Class: ' in class_context:
            class_parts = class_context.split('Class: ')
            if len(class_parts) > 1:
                class_name = class_parts[1].split(',')[0].strip()
        
        # Parse inherited methods
        if 'Inherited Methods: [' in class_context:
            start = class_context.index('Inherited Methods: [') + len('Inherited Methods: [')
            end = class_context.index(']', start)
            inherited_str = class_context[start:end]
            inherited_methods = [m.strip() for m in inherited_str.split(',') if m.strip()]
        
        metadata = {
            'package': package,
            'class_name': class_name,
            'signature': chunk.get('method_signature', ''),
            'method_name': chunk.get('method_name', ''),
            'dependencies': chunk.get('dependency_types', []),
            'inherited_methods': inherited_methods,
            'file_path': file_path or 'unknown'
        }
        
        return metadata
    
    def add_batch(self, enriched_chunks: List[Dict[str, Any]], file_path: Optional[str] = None):
        """
        Add a batch of enriched chunks to the vector store.
        
        Args:
            enriched_chunks: List of enriched code chunks
            file_path: Source file path
        """
        logger.info(f"Adding batch of {len(enriched_chunks)} chunks")
        
        records = []
        
        for chunk in enriched_chunks:
            # Extract metadata
            metadata = self.extract_metadata(chunk, file_path)
            
            # Generate deterministic ID
            chunk_id = self.generate_id(
                metadata['package'],
                metadata['class_name'],
                metadata['signature']
            )
            
            # Build search text
            search_text = self.build_search_text(chunk)
            
            # Serialize metadata to JSON
            metadata_json = json.dumps(metadata)
            
            records.append({
                'id': chunk_id,
                'search_text': search_text,
                'code': chunk.get('method_body', ''),
                'metadata': metadata_json
            })
        
        # Generate embeddings for all search texts
        search_texts = [r['search_text'] for r in records]
        embeddings = self.embed_texts(search_texts)
        
        # Add vectors to records
        for record, embedding in zip(records, embeddings):
            record['vector'] = embedding
        
        # Create or append to table
        if self.table is None:
            # Check if table exists
            try:
                self.table = self.db.open_table(self.table_name)
                logger.info(f"Opened existing table: {self.table_name}")
            except:
                # Create new table with retry logic for Windows file locking
                logger.info(f"Creating new table: {self.table_name}")
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.table = self.db.create_table(
                            self.table_name,
                            data=records,
                            schema=CodeChunkSchema
                        )
                        logger.info(f"Added {len(records)} records to new table")
                        return
                    except Exception as e:
                        if attempt < max_retries - 1 and "being used by another process" in str(e):
                            import time
                            wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                            logger.warning(f"File lock error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)
                        else:
                            raise
        
        # Add to existing table with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.table.add(records)
                logger.info(f"Added {len(records)} records to existing table")
                return
            except Exception as e:
                if attempt < max_retries - 1 and "being used by another process" in str(e):
                    import time
                    wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                    logger.warning(f"File lock error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise
    
    def search(
        self,
        query: str,
        limit: int = 5,
        task: str = "retrieval.query"
    ) -> List[Dict[str, Any]]:
        """
        Search for similar code chunks.
        
        Args:
            query: Search query
            limit: Number of results
            task: Task type for query embedding
            
        Returns:
            List of search results with metadata
        """
        if self.table is None:
            logger.warning("No table exists yet")
            return []
        
        # Embed query
        query_embedding = self.embed_texts([query], task=task)[0]
        
        # Search
        results = self.table.search(query_embedding).limit(limit).to_list()
        
        # Parse metadata JSON
        for result in results:
            if 'metadata' in result:
                result['metadata_parsed'] = json.loads(result['metadata'])
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if self.table is None:
            return {'count': 0, 'table_exists': False}
        
        count = self.table.count_rows()
        return {
            'count': count,
            'table_exists': True,
            'table_name': self.table_name,
            'db_path': str(self.db_path)
        }
