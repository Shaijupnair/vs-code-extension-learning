# Main Ingestion Pipeline Documentation

## Overview

The `main_ingest.py` script orchestrates the complete **two-pass indexing strategy** for Java codebases, handling packages, inheritance, method overloading, and dependencies.

## Two-Pass Strategy

### Pass 1: Hierarchy Scan
**Purpose:** Build complete inheritance map before parsing

**Process:**
1. Scan all Java files
2. Extract class names, parent classes, and public methods
3. Generate `project_hierarchy.json`
4. Creates foundation for context-aware parsing

### Pass 2: Context-Aware Ingestion
**Purpose:** Parse, enrich, and index with full context

**Process:**
1. Load hierarchy map
2. Initialize parser with inheritance context
3. Process files in batches
4. Enrich with LLM summaries
5. Store in vector database

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IngestionPipeline                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: Hierarchy Scan                                    │
│    └─> build_project_map()                                  │
│         └─> project_hierarchy.json                          │
│                                                              │
│  Phase 2: Ingestion Loop                                    │
│    ├─> Find all .java files                                 │
│    ├─> For each file:                                       │
│    │     ├─> Parse (with inheritance context)               │
│    │     ├─> Add to buffer                                  │
│    │     └─> If buffer full:                                │
│    │           ├─> Enrich batch (LLM)                        │
│    │           ├─> Generate embeddings (Jina V3)             │
│    │           └─> Store in LanceDB                          │
│    └─> Progress tracking + error handling                   │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Batch Processing**
- Buffer size: 20 chunks (configurable)
- Reduces API calls
- Optimizes database writes
- Memory efficient

### 2. **Error Handling**
- Try/catch per file
- Logs errors to `ingestion_errors.log`
- **Does not crash** on parser errors
- Continues processing remaining files

### 3. **Progress Tracking**
- Real-time progress bar (tqdm)
- File count
- Success/failure tracking
- Time estimation

### 4. **Logging**
- Dual output: console + file
- Timestamp on all events
- Error details saved
- Final statistics report

### 5. **Graceful Degradation**
- Failed files logged but skipped
- Buffer flushed on shutdown
- Partial results preserved

## Usage

### Basic Usage
```python
from main_ingest import IngestionPipeline
import asyncio

async def main():
    pipeline = IngestionPipeline(
        root_path=r"E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot",
        batch_size=20,
        db_path="./data/lancedb",
        mock_enrichment=False  # Use real OpenAI API
    )
    
    await pipeline.run()

asyncio.run(main())
```

### Configuration Options

**root_path:** Path to Java project root
- Must contain `.java` files
- Can be multi-module project

**batch_size:** Chunks per batch (default: 20)
- Larger = fewer API calls, more memory
- Smaller = more frequent flushes, less memory

**db_path:** Vector database location
- Default: `./data/lancedb`
- Auto-created if doesn't exist

**mock_enrichment:** Use mock summaries (default: False)
- True: No API calls, fast testing
- False: Real OpenAI enrichment

## Output

### Files Created

**project_hierarchy.json**
```json
{
  "com.example.Dog": {
    "parent": "Animal",
    "methods": ["bark", "wagTail", "getBreed"]
  }
}
```

**ingestion.log**
```
2025-12-31 17:49:00 - INFO - PHASE 1: Hierarchy Scan
2025-12-31 17:49:05 - INFO - ✓ Phase 1 Complete: 150 classes
2025-12-31 17:49:06 - INFO - PHASE 2: Ingestion Loop
...
```

**ingestion_errors.log** (if errors occur)
```
[2025-12-31T17:50:00] /path/to/BadFile.java: ParseError: Invalid syntax
```

**data/lancedb/** (vector database)
- Binary format (LanceDB)
- Contains vectors + metadata
- Searchable via VectorStore class

### Final Report

```
================================================================================
Ingestion Complete!
================================================================================
Duration: 0:15:23
Total Files Scanned: 450
Files Processed Successfully: 445
Files Failed: 5
Chunks Indexed: 3,200
Database Records: 3,200
================================================================================
```

## Phase Details

### Phase 1: Hierarchy Scan

**Input:** Java project root
**Output:** `project_hierarchy.json`

**Process:**
1. Walk directory tree
2. For each `.java` file:
   - Extract package + class name
   - Find parent class (extends)
   - List public methods
3. Build JSON map
4. Save to file

**Time:** ~5-30 seconds (depends on project size)

### Phase 2: Ingestion Loop

**Input:** Java files + hierarchy map
**Output:** Populated vector database

**Process per file:**
1. **Parse:**
   - Load hierarchy for this file
   - Extract methods with context
   - Include inherited methods
   
2. **Buffer:**
   - Add chunks to batch
   - Track file path
   
3. **Flush (every 20 chunks):**
   ```python
   # Enrich
   enriched = await enricher.enrich_batch(buffer)
   
   # Store (builds search text + embeds + saves)
   vector_store.add_batch(enriched)
   
   # Clear
   buffer = []
   ```

**Time:** Varies by project size
- Small (100 files): ~2-5 minutes
- Medium (500 files): ~10-20 minutes
- Large (2000+ files): ~1-2 hours

## Error Handling

### File-Level Errors
**Scenario:** Parser crashes on malformed Java

**Handling:**
```python
try:
    chunks = parser.parse_file(file_path)
except Exception as e:
    log_error(file_path, e)  # Log and continue
    files_failed += 1
```

**Result:** Error logged, pipeline continues

### Batch-Level Errors
**Scenario:** Enrichment or storage fails

**Handling:**
```python
try:
    enriched = await enricher.enrich_batch(buffer)
    vector_store.add_batch(enriched)
except Exception as e:
    logger.error(f"Buffer flush failed: {e}")
    # Log all files in buffer
```

**Result:** Entire batch skipped, logged

## Performance

### Speed Factors

**Fast:**
- Mock enrichment (no API)
- GPU available (Jina V3)
- SSD storage (LanceDB)

**Slow:**
- Real enrichment (API network)
- CPU only (slower embeddings)
- HDD storage

### Optimization Tips

1. **Increase batch size** (20 → 50)
   - Fewer API round trips
   - Better throughput

2. **Enable GPU** (auto-detected)
   - 5-10x faster embeddings
   - Requires CUDA

3. **Mock mode for testing**
   - Test pipeline logic quickly
   - Switch to real for production

## Testing

### Test Script
```bash
python test/test_main_ingest.py
```

**Tests:**
- Small dataset (3 files)
- Mock enrichment
- Verifies end-to-end flow
- Checks search functionality

### Manual Test
```bash
python main_ingest.py
```

**Monitors:**
- Progress bar
- Console logs
- Error log file
- Final statistics

## Production Run

### Before Running

1. **Set API key** in `.env`:
   ```
   OPENAI_API_KEY=your-key-here
   ```

2. **Check disk space:**
   - ~200MB per 100,000 methods

3. **Verify project path:**
   - Update `PROJECT_ROOT` in `main_ingest.py`

### Running

```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Run pipeline
python main_ingest.py
```

### Monitoring

- Watch progress bar for completion percentage
- Check `ingestion.log` for detailed progress
- Monitor `ingestion_errors.log` for failures

### After Completion

- Review final statistics
- Check error log if failures > 0
- Test search with queries

## Next Steps

After ingestion completes:

1. **Build Query Interface**
   - Implement RAG query system
   - Handle multi-step lookups
   - Resolve dependencies

2. **Test Search Quality**
   - Run sample queries
   - Verify relevance
   - Tune if needed

3. **Production Deployment**
   - API endpoint
   - VS Code extension integration
   - Caching layer

---

**Status:** ✅ Production Ready  
**Tested:** Yes (with test files)  
**Scalable:** Yes (batching + streaming)
