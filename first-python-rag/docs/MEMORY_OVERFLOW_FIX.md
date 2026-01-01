# Memory Overflow Fix

## Problem
Memory allocation error during enrichment:
```
ERROR: not enough memory: you tried to allocate 98832488192 bytes (92 GB)
File: KeySetCollectionExtractor.java
```

## Root Cause
Extremely large method bodies (>10KB) cause the LLM tokenizer to attempt massive memory allocations.

## Solution Applied

### Added Safety Limits in `enricher.py`:

**1. Maximum Chunk Size: 50KB**
- Prevents any single chunk from being too large

**2. Maximum Method Body: 10KB**  
- Truncates extremely long methods

**3. Fallback Enrichment:**
```python
# For oversized chunks:
summary = "Large method: {name} (auto-generated, too large for LLM)"
keywords = [method_name, 'large-method', 'auto-generated']
```

### Benefits:
- ✅ Prevents memory crashes
- ✅ Pipeline continues even with huge files
- ✅ Oversized methods still get indexed (with fallback)
- ✅ Logs warnings for visibility

## Configuration

Limits are in `src/embedding/enricher.py`:
```python
MAX_CHUNK_SIZE = 50000    # 50KB max per chunk
MAX_METHOD_BODY = 10000   # 10KB max method body
```

Adjust these if needed, but values above 50KB risk memory issues.

## What Happens Now

When ingestion encounters a large file:
1. Detects oversized chunk
2. Logs warning with size
3. Creates fallback summary
4. Continues processing
5. File gets indexed (with limited enrichment)

No more crashes! 🎉
