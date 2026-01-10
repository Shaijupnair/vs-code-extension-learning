# Comprehensive API Reference

Complete guide to all APIs and libraries used in the Java Code RAG System.

---

## Table of Contents

1. [External Libraries](#external-libraries)
   - [Tree-sitter](#tree-sitter)
   - [OpenAI](#openai)
   - [Transformers (Hugging Face)](#transformers-hugging-face)
   - [PyTorch](#pytorch)
   - [LanceDB](#lancedb)
   - [Python-dotenv](#python-dotenv)
   - [TQDM](#tqdm)
2. [Internal Modules](#internal-modules)
   - [Java Parser](#java-parser)
   - [Hierarchy Scanner](#hierarchy-scanner)
   - [Code Enricher](#code-enricher)
   - [Vector Store](#vector-store)
3. [Configuration](#configuration)

---

## External Libraries

### Tree-sitter

**Library:** `tree-sitter` + `tree-sitter-java`

**Purpose:** Parse Java source code into an Abstract Syntax Tree (AST)

**Why We Use It:**
- **Fast:** Written in C, much faster than pure Python parsers
- **Accurate:** Official Java grammar, handles all Java syntax
- **Incremental:** Can update AST on code changes (future feature)
- **Language-agnostic:** Same API for parsing any language

**How We Use It:**

**Location:** `src/parser/java_parser.py`

```python
from tree_sitter import Language, Parser

# Load Java language
Java = Language('resources/wasm/tree-sitter-java.wasm', 'java')
parser = Parser()
parser.set_language(Java)

# Parse Java code
tree = parser.parse(bytes(java_code, 'utf8'))
root_node = tree.root_node
```

**Key Operations:**

1. **Parse File:** Convert Java source to AST
   ```python
   tree = parser.parse(bytes(code, 'utf8'))
   ```

2. **Query Nodes:** Find specific syntax elements
   ```python
   # Find all method declarations
   query = Java.query("(method_declaration) @method")
   captures = query.captures(root_node)
   ```

3. **Extract Text:** Get source code for a node
   ```python
   method_text = code[node.start_byte:node.end_byte]
   ```

**Intent:** We need to understand Java code structure (classes, methods, parameters) without compiling it. Tree-sitter gives us a reliable, fast AST parser.

---

### OpenAI / Ollama

**Libraries:** 
- `openai` (AsyncOpenAI client) - Cloud API
- `httpx` - For Ollama local API

**Purpose:** Generate semantic summaries and keywords for code chunks

**Providers Supported:**
- **OpenAI:** Cloud-based (gpt-4o-mini, gpt-4o) - Paid, best quality
- **Ollama:** Local models (deepseek-coder, codellama) - Free, private

**Why We Use Them:**
- **Understanding:** LLMs understand business logic, not just syntax
- **Semantic Search:** Enriched summaries enable better search results
- **Keywords:** Generate search terms users might actually use
- **Async:** Non-blocking API calls for batch processing
- **Choice:** OpenAI for quality, Ollama for cost/privacy

**How We Use Them:**

**Location:** `src/embedding/enricher.py`

**Provider Selection:**

```python
from openai import AsyncOpenAI
import httpx

# Option 1: OpenAI (configured via config.ini)
enricher = CodeEnricher(
    provider="openai",
    model="gpt-4o-mini"
)

# Option 2: Ollama (configured via config.ini)
enricher = CodeEnricher(
    provider="ollama",
    model="deepseek-coder",
    ollama_base_url="http://localhost:11434"
)
```

---

#### OpenAI API Call Explained

**API Endpoint:** `https://api.openai.com/v1/chat/completions`

**Full API Call:**
```python
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a Java code expert..."
        },
        {
            "role": "user",
            "content": prompt  # Contains code + context
        }
    ],
    response_format={"type": "json_object"},
    temperature=0.3,
    max_tokens=300
)

# Extract response
content = response.choices[0].message.content
enrichment = json.loads(content)
# Returns: {"summary": "...", "keywords": [...]}
```

**Parameter Breakdown:**

| Parameter | Value | Why This Value? |
|-----------|-------|-----------------|
| `model` | `gpt-4o-mini` | **Fast & cheap** (~$0.0004 per method). Good enough for code understanding. Alternative: `gpt-4o` for better quality at 5x cost. |
| `role: system` | `"You are a Java code expert..."` | **Sets context** for the LLM. Tells it to analyze code, not general chat. |
| `role: user` | Contains code + context | **Provides input**. We send: method body + class context + dependencies + inheritance. |
| `response_format` | `{"type": "json_object"}` | **Guarantees valid JSON**. Forces model to return parseable JSON, not plain text. Critical for automation. |
| `temperature` | `0.3` | **Low = consistent**. Range 0-1. Low temp means same code → same summary. High temp = creative but unpredictable. We want consistency. |
| `max_tokens` | `300` | **Limits response length**. ~225 words max. Keeps summaries concise and costs low. Prevents runaway token usage. |

**Why These Settings?**

1. **JSON Format:** We parse the response automatically. Plain text would require complex parsing.
2. **Low Temperature:** Same method should get same summary every time (deterministic).
3. **Token Limit:** Summaries must be short for search. Long responses waste tokens/money.
4. **Async:** We process 20+ methods concurrently. Async = no blocking, faster ingestion.

**Cost Per Method:**
- Input: ~500 tokens (code + context)
- Output: ~100 tokens (summary + keywords)
- Total: ~600 tokens × $0.000015/1K = **$0.00039** per method

**Intent:** We need to convert raw Java code into human-searchable descriptions. OpenAI's GPT models understand code semantics (what it does) not just syntax (how it's written), making search results relevant to user intent.

---

#### Ollama API Call Explained

**API Endpoint:** `http://localhost:11434/api/generate` (Local)

**Full API Call:**
```python
async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-coder",
            "prompt": prompt,  # Contains code + context
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 300
            }
        }
    )

# Extract response
result = response.json()
content = result['response']
enrichment = json.loads(content)
# Returns: {"summary": "...", "keywords": [...]}
```

**Parameter Breakdown:**

| Parameter | Value | Why This Value? |
|-----------|-------|-----------------|
| `model` | `deepseek-coder` | **Code-specialized model**. Trained on code datasets. Free alternative to GPT. Available sizes: 6.7B, 33B. |
| `prompt` | Same as OpenAI | **Context-aware prompt**. Reuses same prompt engineering as OpenAI for consistency. |
| `format` | `"json"` | **Requests JSON output**. Tells Ollama to structure response as JSON. Similar to OpenAI's `response_format`. |
| `stream` | `False` | **Wait for full response**. `True` would stream tokens as they're generated. We want complete response. |
| `timeout` | `60.0` seconds | **Prevents hanging**. Local models can be slow on CPU. 60s is enough for GPU, prevents infinite wait. |
| `temperature` | `0.3` | **Same reasoning as OpenAI**. Low = deterministic, consistent summaries. |
| `num_predict` | `300` | **Max tokens to generate**. Equivalent to OpenAI's `max_tokens`. Keeps responses short. |

**Why These Settings?**

1. **Timeout:** Local inference can be slow (5-10s on CPU, <1s on GPU). Need timeout to avoid hanging.
2. **No Streaming:** Simpler code, easier error handling. Streaming is for interactive chat.
3. **JSON Format:** Must be parseable. Some models ignore this, so we have fallback enrichment.
4. **Same Temp/Tokens:** Consistency with OpenAI. Makes A/B testing fair.

**Performance:**
- **GPU:** ~200ms per method (RTX 4060)
- **CPU:** ~2-5s per method
- **Cost:** $0.00 (free, unlimited)

**Intent:** We want free, unlimited code enrichment that keeps data local. Ollama runs models on your hardware, no API costs, no external data transfer. Quality is 80-90% of GPT-4o-mini, but good enough for code search while being completely free.

---

#### Comparison Table

| Aspect | OpenAI | Ollama |
|--------|--------|--------|
| **Cost** | ~$0.0004/method | Free |
| **Speed** | ~500ms | ~200ms (GPU), 2s (CPU) |
| **Quality** | Best (GPT-4o) | Very Good (DeepSeek) |
| **Privacy** | Data sent to OpenAI | Stays local |
| **Limits** | 3,500 TPM rate limit | None |
| **Setup** | API key only | Install Ollama + model |
| **Offline** | ❌ No | ✅ Yes |

**When to Use Each:**

**Use OpenAI if:**
- You need absolute best quality
- You're okay with API costs (~$4 per 10K methods)
- You want consistent cloud performance
- Privacy isn't a concern

**Use Ollama if:**
- You want free unlimited enrichment
- You have GPU (RTX 3060 or better)
- Privacy matters (proprietary code)
- You're indexing 100K+ methods (saving $40+)

**Intent Summary:** By supporting both providers, we give users flexibility: pay for quality (OpenAI) or get good-enough results for free (Ollama). Configuration is identical - just change 2 lines in config.ini.

---

**Key Parameters:**

- **model:** `gpt-4o-mini` (OpenAI) or `deepseek-coder` (Ollama)
- **response_format / format:** `json_object` / `json` (ensures parseable output)
- **response_format:** `json_object` (ensures valid JSON)
- **temperature:** `0.3` (low = consistent, high = creative)
- **max_tokens:** `300` (limit response length)

**Our Prompt Structure:**

```
System: You are a Java code expert
User: 
  Package: com.example
  Class Context: MyClass extends Parent
  Signature: public void doSomething(String param)
  Dependencies: [Widget, Transaction]
  Code: <actual code>
  
  Task: Generate 1-sentence summary + 3-5 keywords
  Output: JSON { "summary": "...", "keywords": [...] }
```

**Intent:** Raw code isn't searchable by business intent. We use GPT to translate code into human-readable summaries that users can search for (e.g., "validate transaction" instead of "boolean check(String id)").

---

### Transformers (Hugging Face)

**Library:** `transformers` (AutoModel)

**Purpose:** Load and run Jina V3 embedding model

**Why We Use It:**
- **Standard API:** Works with thousands of models
- **Local Execution:** Run models offline (no API calls)
- **GPU Support:** Automatic CUDA acceleration
- **Model Hub:** Easy to download and cache models

**How We Use It:**

**Location:** `src/database/vector_store.py`

```python
from transformers import AutoModel

# Load Jina V3 model
model = AutoModel.from_pretrained(
    "C:\\models\\huggingface\\JinaV3\\jina-embeddings-v3",
    trust_remote_code=True  # Required for Jina V3
)

# Move to GPU if available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
model.eval()  # Set to inference mode
```

**Key API Calls:**

1. **Load Model:**
   ```python
   AutoModel.from_pretrained(model_path, trust_remote_code=True)
   ```

2. **Generate Embeddings:**
   ```python
   embeddings = model.encode(
       texts,
       task="retrieval.passage",  # Jina-specific
       device=device
   )
   ```

**Jina V3 Specific:**

- **Task Parameter:** `retrieval.passage` for indexing, `retrieval.query` for searching
- **Dimensions:** 1024-dim vectors
- **Trust Remote Code:** Jina V3 has custom code in the model

**Intent:** We need to convert text into vectors for semantic search. Transformers library provides a standard way to load and use the Jina V3 model locally with GPU acceleration.

---

### PyTorch

**Library:** `torch`

**Purpose:** GPU acceleration for embedding generation

**Why We Use It:**
- **GPU Support:** CUDA acceleration (10x faster)
- **Tensor Operations:** Efficient batch processing
- **Model Backend:** Used by Transformers library
- **Memory Management:** Efficient GPU memory handling

**How We Use It:**

**Location:** `src/database/vector_store.py`

```python
import torch

# Check GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Move model to GPU
model.to(device)

# Inference mode (no gradients)
with torch.no_grad():
    embeddings = model.encode(texts, device=device)

# Convert to numpy
embeddings_np = embeddings.cpu().numpy()
```

**Key Operations:**

1. **Device Management:**
   ```python
   torch.cuda.is_available()  # Check GPU
   tensor.to('cuda')          # Move to GPU
   tensor.cpu()               # Move to CPU
   ```

2. **No Gradient Context:**
   ```python
   with torch.no_grad():
       # Inference only, saves memory
       output = model(input)
   ```

3. **Tensor Conversion:**
   ```python
   numpy_array = torch_tensor.cpu().numpy()
   ```

**Intent:** Embedding 1000s of code chunks is computationally expensive. PyTorch with CUDA lets us use the GPU for ~10x speed improvement over CPU.

---

### LanceDB

**Library:** `lancedb`

**Purpose:** Vector database for storing and searching code embeddings

**Why We Use It:**
- **Columnar Storage:** Efficient for large datasets
- **No Server:** Embedded database (just files)
- **Fast Search:** Optimized vector similarity
- **Pydantic Schema:** Type-safe schema definition
- **Incremental Updates:** Can add data without rebuilding

**How We Use It:**

**Location:** `src/database/vector_store.py`

```python
import lancedb
from lancedb.pydantic import LanceModel, Vector
from pydantic import Field

# Define schema
class CodeChunkSchema(LanceModel):
    id: str
    vector: Vector(1024)  # Jina V3 dimension
    code: str
    search_text: str
    metadata: str  # JSON string

# Connect to database
db = lancedb.connect("./data/lancedb")

# Create table
table = db.create_table(
    "code_chunks",
    data=records,
    schema=CodeChunkSchema
)

# Add more data
table.add(new_records)

# Search
results = table.search(query_vector).limit(5).to_list()
```

**Key Operations:**

1. **Create/Open Database:**
   ```python
   db = lancedb.connect(db_path)
   table = db.open_table(table_name)
   ```

2. **Insert Data:**
   ```python
   table.add([
       {"id": "123", "vector": [...], "code": "...", ...}
   ])
   ```

3. **Vector Search:**
   ```python
   results = table.search(query_embedding).limit(k).to_list()
   # Returns: [{"id": "...", "vector": [...], "_distance": 0.23, ...}]
   ```

4. **Metadata:**
   ```python
   count = table.count_rows()
   ```

**Schema Design:**

```python
# Our schema stores:
- id: SHA256 hash (package + class + signature)
- vector: 1024-dim embedding
- code: Raw method body
- search_text: Summary + keywords + signature
- metadata: JSON with package, dependencies, inheritance
```

**Intent:** We need persistent storage for millions of code chunks with fast similarity search. LanceDB provides an embedded vector database optimized for this use case.

---

### Python-dotenv

**Library:** `python-dotenv`

**Purpose:** Load environment variables from `.env` file

**Why We Use It:**
- **Security:** Keep API keys out of code
- **Portability:** Same code works across machines
- **Standard:** Industry best practice
- **Simple:** Just one function call

**How We Use It:**

**Location:** `src/embedding/enricher.py`, `search.py`

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
api_key = os.getenv("OPENAI_API_KEY")
```

**.env File:**
```
OPENAI_API_KEY=sk-your-key-here
```

**Intent:** API keys shouldn't be in code or git. `.env` file provides a secure, standard way to manage secrets locally.

---

### TQDM

**Library:** `tqdm`

**Purpose:** Progress bars for long-running operations

**Why We Use It:**
- **User Experience:** Shows progress, not stuck
- **ETA:** Estimates remaining time
- **Simple:** One line of code
- **Works Everywhere:** Terminal, notebook, GUI

**How We Use It:**

**Location:** `main_ingest.py`

```python
from tqdm import tqdm

# Wrap iterator
with tqdm(total=len(files), desc="Processing", unit="file") as pbar:
    for file in files:
        # Process file
        process(file)
        
        # Update progress
        pbar.update(1)
```

**Output:**
```
Processing files: 42%|████████░░░░░░| 450/1070 [15:23<21:45, 2.1file/s]
```

**Intent:** Ingesting 1000+ files takes time. Progress bars show users that the system is working and how long to wait.

---

## Internal Modules

### Java Parser

**Module:** `src/parser/java_parser.py`

**Class:** `JavaCodeParser`

**Purpose:** Extract structured information from Java source files

**Key Methods:**

#### `__init__(hierarchy_map_path)`

**Purpose:** Initialize parser with inheritance context

```python
parser = JavaCodeParser(hierarchy_map_path="project_hierarchy.json")
```

**Parameters:**
- `hierarchy_map_path`: Path to JSON with inheritance info

**Why:** Inheritance context is needed to know which methods are inherited.

---

#### `parse_file(file_path) -> List[Dict]`

**Purpose:** Parse a Java file and extract all methods/constructors

```python
chunks = parser.parse_file("MyClass.java")
# Returns list of dictionaries, one per method
```

**Returns:** List of chunks, each containing:
```python
{
    'method_name': 'doSomething',
    'method_signature': 'public void doSomething(String param)',
    'method_body': '...',
    'class_context': 'Package: com.example, Class: MyClass, Extends: Parent, Inherited Methods: [eat, sleep]',
    'dependency_types': ['Widget', 'Transaction'],
    'id': 'sha256_hash_of_context_and_signature'
}
```

**Intent:** Convert raw Java files into structured data that can be enriched and indexed.

---

#### `_extract_package_name(tree)` (Private)

**Purpose:** Find package declaration

```python
# Looks for: package com.example.util;
package = self._extract_package_name(tree)
# Returns: "com.example.util"
```

**Why:** Package distinguishes classes with same name.

---

#### `_get_inherited_methods(class_name)` (Private)

**Purpose:** Recursively get all inherited method names

```python
inherited = self._get_inherited_methods("Dog")
# Returns: ['eat', 'sleep', 'getName', 'makeSound']  # from Animal
```

**Why:** Users search for inherited methods too, so we need to include them in context.

---

#### `_extract_dependency_types(params_node)` (Private)

**Purpose:** Extract custom types from method parameters

```python
# Method: public void process(Transaction t, Widget w, int count)
deps = self._extract_dependency_types(params_node)
# Returns: ['Transaction', 'Widget']  # Excludes primitives
```

**Why:** Helps users understand what objects a method needs.

---

### Hierarchy Scanner

**Module:** `src/parser/hierarchy_scanner.py`

**Function:** `build_project_map(root_path, output_path)`

**Purpose:** Scan Java project and build inheritance map (Phase 1)

```python
hierarchy_map = build_project_map(
    root_path="E:\\project\\src",
    output_path="project_hierarchy.json"
)
```

**Output Format:**
```json
{
  "com.example.Dog": {
    "parent": "Animal",
    "methods": ["bark", "wagTail", "getBreed"]
  },
  "com.example.Animal": {
    "parent": null,
    "methods": ["eat", "sleep", "getName", "makeSound"]
  }
}
```

**Why:** We need to know inheritance relationships before parsing individual files, so we can inject inherited methods into class context.

---

### Code Enricher

**Module:** `src/embedding/enricher.py`

**Class:** `CodeEnricher`

**Purpose:** Generate LLM summaries and keywords for code chunks

**Key Methods:**

#### `__init__(api_key, model, mock_mode)`

**Purpose:** Initialize enricher

```python
enricher = CodeEnricher(
    api_key=None,  # Uses OPENAI_API_KEY from .env
    model="gpt-4o-mini",
    mock_mode=False  # True = no API calls
)
```

**Why:** Mock mode for testing without API costs.

---

#### `enrich_batch(chunks) -> List[Dict]`

**Purpose:** Enrich multiple chunks concurrently

```python
enriched = await enricher.enrich_batch([
    {'method_name': 'validate', 'method_body': '...', ...},
    {'method_name': 'process', 'method_body': '...', ...}
])
```

**Returns:** Same chunks with added fields:
```python
{
    # Original fields...
    'summary': "Validates transaction based on business rules",
    'keywords': ['validate', 'transaction', 'verification', 'rules']
}
```

**Intent:** Batch processing with asyncio for speed.

---

#### `_build_prompt(chunk)` (Private)

**Purpose:** Construct context-aware prompt for LLM

```python
prompt = self._build_prompt(chunk)
```

**Prompt Template:**
```
Package: com.example
Class Context: MyClass extends Parent, Inherited: [eat, sleep]
Signature: public void validate(Transaction t)
Dependencies: Transaction
Code: <actual code>

Task: 1-sentence summary + 3-5 keywords
Output: {"summary": "...", "keywords": [...]}
```

**Why:** Rich context helps LLM understand code better than just seeing the code body.

---

### Vector Store

**Module:** `src/database/vector_store.py`

**Class:** `VectorStore`

**Purpose:** Manage vector database operations

**Key Methods:**

#### `__init__(db_path, model_path, use_gpu)`

**Purpose:** Initialize database and embedding model

```python
store = VectorStore(
    db_path="./data/lancedb",
    model_path="C:\\models\\...\\jina-embeddings-v3",
    use_gpu=True
)
```

**Why:** Loads heavy models once, reuses for all operations.

---

#### `add_batch(enriched_chunks)`

**Purpose:** Index a batch of enriched code chunks

```python
store.add_batch([
    {'method_name': 'validate', 'summary': '...', 'keywords': [...], ...}
])
```

**Process:**
1. Extract metadata (package, dependencies, etc.)
2. Generate deterministic ID (SHA256 hash)
3. Build search_text (summary + keywords + signature)
4. Embed search_text → vector
5. Store in LanceDB

**Why:** Batching is more efficient than one-by-one.

---

#### `search(query, limit, task) -> List[Dict]`

**Purpose:** Search for similar code chunks

```python
results = store.search(
    query="how to validate transaction",
    limit=5,
    task="retrieval.query"  # Jina-specific
)
```

**Returns:**
```python
[
    {
        'id': '...',
        'vector': [...],
        'code': 'public void validate() {...}',
        'search_text': 'Summary: ... | Keywords: ...',
        'metadata': '{"package": "...", "dependencies": [...]}',
        'metadata_parsed': {...},
        '_distance': 0.23  # Lower = more similar
    }
]
```

**Why:** Converts text query to vector, finds nearest neighbors.

---

#### `embed_texts(texts, task)`

**Purpose:** Generate embeddings using Jina V3

```python
vectors = store.embed_texts(
    texts=["validate transaction", "process payment"],
    task="retrieval.passage"  # or "retrieval.query"
)
```

**Task Types:**
- `retrieval.passage`: For indexing (storage)
- `retrieval.query`: For searching

**Why:** Jina V3 uses task-specific embeddings for better results.

---

#### `generate_id(package, class_name, signature)`

**Purpose:** Create deterministic unique ID

```python
id = store.generate_id(
    package="com.example",
    class_name="Calculator",
    signature="public int add(int a, int b)"
)
# Returns: "a7f3bc...289d" (SHA256 hash)
```

**Why:** Handles overloading and same class names in different packages.

---

## Configuration

### config.ini

**Purpose:** Centralized configuration for all settings

**Sections:**

#### [Paths]
```ini
project_root = E:\OpenSource\eclipse\swtbot
database_path = ./data/lancedb
jina_model_path = C:\models\huggingface\JinaV3\jina-embeddings-v3
```

**Why:** Easy to change target project without editing code.

---

#### [Ingestion]
```ini
batch_size = 20
mock_enrichment = False
enrichment_model = gpt-4o-mini
```

**Why:** Tune performance vs cost.

---

#### [Search]
```ini
use_query_expansion = True
search_results_limit = 5
query_expansion_model = gpt-4o-mini
```

**Why:** Enable/disable features without code changes.

---

## API Usage Flow

### Ingestion Pipeline

```
1. Load config.ini
   ↓
2. Build hierarchy map (hierarchy_scanner)
   ↓
3. For each Java file:
   ├─ Parse with tree-sitter → chunks
   ├─ Enrich with OpenAI → summaries
   ├─ Embed with Jina V3 → vectors
   └─ Store in LanceDB
   ↓
4. Database ready for search
```

### Search Pipeline

```
1. User query: "How to click a widget?"
   ↓
2. Expand query with OpenAI (optional)
   ↓
3. Embed query with Jina V3 (task="retrieval.query")
   ↓
4. Search LanceDB for similar vectors
   ↓
5. Return top-K results with metadata
```

---

## Design Decisions

### Why These Libraries?

**Tree-sitter:** Most accurate, fastest Java parser
**OpenAI:** Best LLM for code understanding
**Jina V3:** State-of-art embeddings, works offline
**PyTorch:** Industry standard for ML, GPU support
**LanceDB:** Embedded, fast, no server needed

### Why This Architecture?

**Two-Pass:** Hierarchy first, then parse (inheritance context)
**Batch Processing:** Faster than one-by-one
**Async:** Non-blocking LLM calls
**Single Writer:** Prevents file locking on Windows
**Deterministic IDs:** Handles overloading + namespaces

---

## Further Reading

### Official Documentation

- **Tree-sitter:** https://tree-sitter.github.io/tree-sitter/
- **OpenAI:** https://platform.openai.com/docs/api-reference
- **Transformers:** https://huggingface.co/docs/transformers
- **PyTorch:** https://pytorch.org/docs/
- **LanceDB:** https://lancedb.github.io/lancedb/
- **Jina V3:** https://huggingface.co/jinaai/jina-embeddings-v3

### Our Documentation

- **Parser:** `docs/PARSER_SUMMARY.md`
- **Enrichment:** `docs/CONTEXT_AWARE_ENRICHMENT.md`
- **Database:** `docs/VECTOR_DATABASE_IMPLEMENTATION.md`
- **Pipeline:** `docs/INGESTION_PIPELINE.md`
- **Search:** `docs/SEARCH_INTERFACE.md`

---

**Last Updated:** 2026-01-02
