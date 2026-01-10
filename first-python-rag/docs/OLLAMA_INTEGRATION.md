# Ollama Integration Guide

## Overview

The RAG system now supports **local LLM enrichment** via Ollama, giving you a free alternative to OpenAI. DeepSeek Coder is recommended for code understanding.

## Why Ollama + Deep Seek Coder?

**DeepSeek Coder Benefits:**
- ✅ **Free:** No API costs
- ✅ **Fast:** Runs locally on your GPU
- ✅ **Code-Specialized:** Trained specifically for code
- ✅ **Private:** No data leaves your machine  
- ✅ **Unlimited:** No rate limits

**vs OpenAI:**
| Feature | OpenAI | Ollama + DeepSeek |
|---------|--------|-------------------|
| Cost | $0.15-$0.60 per 1M tokens | Free |
| Speed | API latency (~500ms) | Local (~200ms on GPU) |
| Privacy | Data sent to OpenAI | Stays local |
| Rate Limits | Yes (3,500 TPM) | None |
| Quality | Excellent | Very good for code|

## Setup

### 1. Install Ollama

**Download:** https://ollama.com/download

**Verify Installation:**
```powershell
ollama --version
# Should show: ollama version 0.x.x
```

### 2. Download DeepSeek Coder

```powershell
ollama pull deepseek-coder
```

**Other Good Code Models:**
```powershell
ollama pull codellama      # Meta's code model
ollama pull llama3          # General purpose
ollama pull qwen2.5-coder   # Alibaba's code model
```

### 3. Verify Ollama is Running

```powershell
# Test endpoint
curl http://localhost:11434/api/tags

# Should return JSON with available models
```

### 4. Configure RAG System

Edit `config.ini`:
```ini
[Ingestion]
# Switch from OpenAI to Ollama
llm_provider = ollama

# Use DeepSeek Coder
enrichment_model = deepseek-coder

# Ollama server URL (default)
ollama_base_url = http://localhost:11434
```

### 5. Run Ingestion

```bash
python main_ingest.py
```

**You'll see:**
```
INFO: Connected to Ollama at http://localhost:11434
INFO: Using model: deepseek-coder
INFO: ✓ Enricher initialized (provider=ollama, model=deepseek-coder)
```

## Configuration Options

### config.ini Settings

```ini
[Ingestion]
# Provider: "openai" or "ollama"
llm_provider = ollama

# Model name
# For Ollama: deepseek-coder, codellama, llama3, qwen2.5-coder
# For OpenAI: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
enrichment_model = deepseek-coder

# Ollama server (only used if provider=ollama)
ollama_base_url = http://localhost:11434

# Mock mode (skips LLM entirely)
mock_enrichment = False
```

### Switch Between Providers

**Use Ollama (Free):**
```ini
llm_provider = ollama
enrichment_model = deepseek-coder
```

**Use OpenAI (Higher Quality):**
```ini
llm_provider = openai
enrichment_model = gpt-4o-mini
```

**No Enrichment (Testing):**
```ini
mock_enrichment = True
```

## Model Recommendations

### For Code Enrichment

**Best FREE:**
```
deepseek-coder (6.7B or 33B)
- Specialized for code
- Fast inference
- Good understanding of Java
```

**Alternative FREE:**
```
codellama (7B or 13B)
- Meta's code model
- Slightly faster
- Good for simple code
```

**Best PAID:**
```
gpt-4o-mini (OpenAI)
- Best code understanding
- Most accurate summaries
- Costs ~$0.0004 per method
```

### Model Size Guide

| Model | Size | RAM Needed | Speed | Quality |
|-------|------|------------|-------|---------|
| deepseek-coder:6.7b | 4.2GB | 8GB+ | Fast | Good |
| deepseek-coder:33b | 19GB | 32GB+ | Slow | Excellent |
| codellama:7b | 4.1GB | 8GB+ | Fast | Good |
| llama3:8b | 4.7GB | 8GB+ | Fast | General |

## How It Works

### Architecture

```
Chunk → Enricher → Provider Check
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
[OpenAI API]      [Ollama Local]
gpt-4o-mini       deepseek-coder
    ↓                   ↓
    └─────────┬─────────┘
              ↓
      Enriched Chunk
```

### Ollama Integration

**1. Connection Test (Startup):**
```python
response = requests.get("http://localhost:11434/api/tags")
# Checks if Ollama is running
```

**2. Enrichment Request:**
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-coder",
            "prompt": context_aware_prompt,
            "format": "json",
            "temperature": 0.3
        }
    )
```

**3. Parse Response:**
```python
content = response.json()['response']
enrichment = json.loads(content)
# {"summary": "...", "keywords": [...]}
```

## Troubleshooting

### Ollama Not Found

**Error:**
```
WARNING: Failed to connect to Ollama: ... Running in mock mode.
```

**Fix:**
```powershell
# Start Ollama service
ollama serve

# Or restart Ollama app
```

### Model Not Available

**Error:**
```
Ollama API error 404: model 'deepseek-coder' not found
```

**Fix:**
```powershell
# Download the model
ollama pull deepseek-coder

# List available models
ollama list
```

### Slow Performance

**Problem:** Ollama taking 5-10 seconds per method

**Fix:**
1. **Use smaller model:**
   ```ini
   enrichment_model = deepseek-coder:6.7b
   ```

2. **Reduce context:**
   - Ollama includes full inheritance context
   - Larger context = slower inference

3. **Check GPU usage:**
   ```powershell
   nvidia-smi
   # Ollama should show ~80% GPU usage
   ```

### JSON Parse Errors

**Error:**
```
JSON parsing error for chunk X: Expecting value...
```

**Why:** Model didn't return valid JSON

**Fix:** Model needs better prompting, or fallback enrichment is used

## Performance Comparison

### Speed (per method)

| Provider | Model | Speed | Total (1000 methods) |
|----------|-------|-------|---------------------|
| Ollama | deepseek-coder:6.7b (GPU) | ~200ms | ~3.3 minutes |
| Ollama | deepseek-coder:6.7b (CPU) | ~2s | ~33 minutes |
| OpenAI | gpt-4o-mini | ~500ms | ~8.3 minutes |
| OpenAI | gpt-4o | ~800ms | ~13.3 minutes |

### Cost (1000 methods)

| Provider | Model | Cost |
|----------|-------|------|
| Ollama | Any | $0.00 |
| OpenAI | gpt-4o-mini | ~$0.40 |
| OpenAI | gpt-4o | ~$2.00 |

### Quality

| Provider | Model | Summary Quality | Keyword Quality |
|----------|-------|----------------|-----------------|
| OpenAI | gpt-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| OpenAI | gpt-4o-mini | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Ollama | deepseek-coder:33b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Ollama | deepseek-coder:6.7b | ⭐⭐⭐ | ⭐⭐⭐ |
| Ollama | codellama | ⭐⭐⭐ | ⭐⭐⭐ |

## Recommendation

**For Most Users:**
```ini
llm_provider = ollama
enrichment_model = deepseek-coder
```
- Free
- Good quality
- Fast enough

**For Best Quality:**
```ini
llm_provider = openai
enrichment_model = gpt-4o-mini
```
- Small cost (~$0.40 per 1000 methods)
- Best summaries
- Best keywords

**For Testing:**
```ini
mock_enrichment = True
```
- Instant
- No dependencies
- Basic fallback enrichment

## Example Output

### DeepSeek Coder (Ollama)

**Input:** `public void validateTransaction(Transaction t)`

**Output:**
```json
{
  "summary": "Validates a transaction object by checking its status, amount, and user permissions",
  "keywords": ["validate", "transaction", "verify", "check", "business-rules"]
}
```

### GPT-4o-mini (OpenAI)

**Input:** Same method

**Output:**
```json
{
  "summary": "Validates the transaction state, performing checks on amount limits, user authorization, and fraud detection",
  "keywords": ["validate", "transaction", "authorization", "fraud-detection", "business-logic"]
}
```

**Difference:** GPT-4o-mini provides slightly more detailed summaries and domain-specific keywords.

## Migration Guide

### From OpenAI to Ollama

1. **Install Ollama:**
   ```powershell
   winget install Ollama.Ollama
   ```

2. **Download model:**
   ```powershell
   ollama pull deepseek-coder
   ```

3. **Update config:**
   ```ini
   llm_provider = ollama
   enrichment_model = deepseek-coder
   ```

4. **Delete old database** (optional - only if you want to re-enrich):
   ```powershell
   Remove-Item -Recurse data\lancedb
   ```

5. **Run ingestion:**
   ```bash
   python main_ingest.py
   ```

### Cost Savings

**Before (OpenAI):**
- 10,000 methods × $0.0004 = **$4.00**

**After (Ollama):**
- 10,000 methods × $0.00 = **$0.00**

**Savings:** 100%

---

**Status:** ✅ Implemented and Ready to Use
**Recommended:** Use Ollama for free, unlimited enrichment
