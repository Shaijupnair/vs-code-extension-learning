# Configuration Guide

All hardcoded paths and settings have been moved to `config.ini`.

## Quick Setup

1. **Edit `config.ini`** - Update these key settings:

```ini
[Paths]
# Change this to your Java project
project_root = E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot

# Database location (usually leave as-is)
database_path = ./data/lancedb
```

2. **Run ingestion:**
```bash
python main_ingest.py
```

3. **Run search:**
```bash
python search.py
```

## Configuration Sections

### [Paths]
- `project_root` - Java project to index
- `database_path` - Where to store vector DB
- `jina_model_path` - Local Jina V3 model location

### [Ingestion]
- `batch_size` - Chunks per batch (20 = good default)
- `mock_enrichment` - True = no API calls, False = use OpenAI
- `enrichment_model` - OpenAI model (gpt-4o-mini recommended)

### [Search]
- `use_query_expansion` - True = better results, False = faster
- `search_results_limit` - Number of results (5 = good default)
- `query_expansion_model` - OpenAI model for query expansion

### [Logging]
- `ingestion_log` - Main log file
- `error_log` - Error log file

## Common Configurations

### Test Mode (Fast, No API Costs)
```ini
[Paths]
project_root = E:\Learn_Vs_Code_Extension\first-python-rag\test\dependency_test

[Ingestion]
mock_enrichment = True
```

### Production Mode (Full SWTBot)
```ini
[Paths]
project_root = E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot

[Ingestion]
mock_enrichment = False
batch_size = 20
```

### Fast Search (No Query Expansion)
```ini
[Search]
use_query_expansion = False
search_results_limit = 10
```

## No More Code Editing!

All configuration is now in `config.ini`. Just edit that file and run the scripts.
