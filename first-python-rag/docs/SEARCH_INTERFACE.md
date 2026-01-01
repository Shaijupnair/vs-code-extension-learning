# Search Interface Documentation

## Overview

The `search.py` script provides an interactive **RAG search interface** for querying the Java code knowledge base with query expansion and formatted results.

## Features

### 1. **Query Expansion**
Uses LLM to generate 2-3 query variations for better recall.

**Example:**
```
Original: "How do I click a widget?"
Variations:
  1. "How to select a UI control programmatically?"
  2. "Activate widget interaction methods"
  3. "Click button or component in SWT"
```

### 2. **Semantic Search**
- Uses Jina V3 with `task="retrieval.query"`
- Finds semantically similar code
- Deduplicates results across query variations

### 3. **Formatted Results**
Displays for each result:
- ✅ Relevance score (percentage)
- ✅ Package name
- ✅ Method signature
- ✅ File path
- ✅ LLM-generated summary
- ✅ Dependencies (if any)
- ✅ Inherited methods (if any)
- ✅ Full code snippet

## Usage

### Interactive Mode
```bash
python search.py
```

**Interactive Session:**
```
🔍 Query: How do I click a widget?

   Expanding query...
   Variations: 3
     1. "How do I click a widget?"
     2. "Select UI control interaction"
     3. "Activate widget click event"

📋 Found 5 results:

================================================================================
Result #1 - click
================================================================================

📊 Relevance Score: 87%
📦 Package: org.eclipse.swtbot.swt.finder
✍️  Signature: public void click()
📁 File: /path/to/SWTBotWidget.java

💡 Summary:
Simulates a mouse click action on the widget

💻 Code:
```java
public void click() {
    asyncExec(new VoidResult() {
        public void run() {
            widget.notifyListeners(SWT.MouseDown, createEvent());
            widget.notifyListeners(SWT.MouseUp, createEvent());
        }
    });
}
```
```

### Command Line Mode
```bash
python search.py "How do I click a widget?"
```

Runs single query and exits.

## Architecture

```
┌─────────────────────────────────────┐
│      CodeSearchEngine               │
├─────────────────────────────────────┤
│  Query Input                        │
│    └─> expand_query() [Optional]    │
│         └─> LLM generates variations│
│                                      │
│  For each query variation:          │
│    ├─> Embed with Jina V3            │
│    │    (task="retrieval.query")     │
│    ├─> Search LanceDB                │
│    └─> Collect results               │
│                                      │
│  Deduplicate & Sort                 │
│    └─> By distance (similarity)     │
│                                      │
│  Format & Display                   │
│    └─> Formatted output with        │
│         score, summary, code, etc.   │
└─────────────────────────────────────┘
```

## Query Expansion

### How It Works

**LLM Prompt:**
```
You are helping expand a search query for a Java code search engine.

Original query: "How do I click a widget?"

Generate 2-3 alternative phrasings...
Focus on:
- Technical synonyms
- Different abstraction levels
- Common Java terminology
```

**Response:**
```json
[
  "Select UI control interaction",
  "Activate widget click event",
  "Trigger mouse click on SWT widget"
]
```

### Benefits

- **Better Recall:** Finds relevant code with different terminology
- **Synonym Handling:** "click" → "select", "activate", "trigger"
- **Abstraction Levels:** "widget" → "UI control", "component", "element"

## Result Formatting

### Score Calculation
```python
distance = result.get('_distance', 0)
score = max(0, 1 - distance)  # Inverse of distance
```

- Higher score = more relevant
- Displayed as percentage (e.g., 87%)

### Summary Extraction
Parsed from `search_text` field:
```
Summary: Simulates a mouse click action on the widget | ...
```

### Dependencies Display
```
🔗 Dependencies: Transaction, Widget
```

Shows custom types method depends on.

### Inherited Methods Display
```
👨‍👦 Inherited Methods: [start, stop, validate (+2 more)]
```

Shows first 5 inherited methods.

## Configuration

### In Code
```python
search_engine = CodeSearchEngine(
    db_path="./data/lancedb",      # Database location
    use_query_expansion=True,       # Enable LLM expansion
    model="gpt-4o-mini"            # Model for expansion
)
```

### Environment Variables
```bash
OPENAI_API_KEY=your-key-here  # For query expansion
```

## Examples

### Example 1: Finding Transaction Processing
```
Query: "process transaction"

Result #1 - processTransaction
📊 Relevance Score: 92%
📦 Package: com.example.business
✍️  Signature: public void processTransaction(Transaction t)
💡 Summary: Processes a transaction and validates it before execution
🔗 Dependencies: Transaction
```

### Example 2: Finding Constructors
```
Query: "initialize calculator"

Result #1 - <Constructor>
📊 Relevance Score: 85%
📦 Package: com.example.math
✍️  Signature: public <Constructor> Calculator(int precision)
💡 Summary: Initializes calculator with specified precision
```

### Example 3: Finding with Inheritance
```
Query: "dog bark"

Result #1 - bark
📊 Relevance Score: 95%
📦 Package: com.example.animals
✍️  Signature: public void bark()
👨‍👦 Inherited Methods: [eat, sleep, getName, makeSound]
💡 Summary: Makes the dog bark with specific sound
```

## Performance

**Query Time Breakdown:**
- Query expansion: ~500-1000ms (if enabled)
- Embedding: ~50-100ms (GPU)
- Search: ~10-50ms
- **Total: ~1-2 seconds with expansion**

**Without Expansion:**
- **Total: ~100-200ms**

## Error Handling

### No API Key
```
⚠️  No API key found, query expansion disabled
```
Falls back to single query.

### Expansion Failure
```
⚠️  Query expansion failed: [error], using original
```
Continues with original query.

### No Results
```
No results found. Try a different query.
```

## Advanced Usage

### Custom Limit
```python
results = await search_engine.search(query, limit=10)
```

### Disable Expansion
```python
results = await search_engine.search(query, expand=False)
```

### Programmatic Use
```python
from search import CodeSearchEngine

search_engine = CodeSearchEngine()
results = await search_engine.search("my query", limit=5)

for result in results:
    print(f"Found: {result['metadata_parsed']['method_name']}")
    print(f"Code: {result['code']}")
```

## Testing

### Run Test
```bash
python test/test_search.py
```

Tests with pre-indexed test data.

### Sample Output
```
Testing Query: "create transaction"

Result #1 - createTransaction
📊 Relevance Score: 88%
📦 Package: com.example.transactions
✍️  Signature: public Transaction createTransaction(String id, Widget w)
...
```

## Integration

### VS Code Extension
```javascript
// Call Python search script
const { spawn } = require('child_process');
const python = spawn('python', ['search.py', userQuery]);

python.stdout.on('data', (data) => {
  // Parse and display results
});
```

### API Endpoint
```python
from fastapi import FastAPI
from search import CodeSearchEngine

app = FastAPI()
search_engine = CodeSearchEngine()

@app.get("/search")
async def search(q: str, limit: int = 5):
    results = await search_engine.search(q, limit=limit)
    return {"results": results}
```

## Tips

### Better Queries
- ✅ **Good:** "How do I validate a transaction?"
- ✅ **Good:** "Find perspective by label"
- ❌ **Bad:** "code"
- ❌ **Bad:** "java"

### Use Natural Language
Works better than keywords:
- ✅ "How do I click a button?"
- ❌ "click button method"

### Be Specific
- ✅ "Process payment transaction"
- ❌ "Process"

---

**Status:** ✅ Complete and Tested  
**Query Expansion:** Supported (requires API key)  
**Interactive Mode:** Supported
