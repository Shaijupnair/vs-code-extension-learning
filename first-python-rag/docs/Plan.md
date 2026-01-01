This is a sophisticated RAG architecture that treats code as structural data rather than plain text. To build this successfully with an AI coding agent like Antigravity (or Cursor/Windsurf), you need to break the complex architecture into isolated, verifiable coding tasks.

Here is the step-by-step instruction manual to guide your AI agent.

### **Prerequisites & Context for the Agent**

* **Project Root:** `E:\Learn_Vs_Code_Extension\first-python-rag`
* **Source Code Path:** `E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot`
* **Embedding Model Path:** `C:\models\huggingface\JinaV3\jina-embeddings-v3`
* **Core Tech:** Python, Tree-sitter (Java), LanceDB, Transformers (for Jina).

---

### **Step 1: Environment Setup & Verification**

**Goal:** Initialize the project, create the virtual environment, and verify that the local Jina model can be loaded before we write any complex logic.

**Prompt for Antigravity:**

```markdown
I need to initialize a RAG project for a Java codebase. Please perform the following setup tasks in `E:\Learn_Vs_Code_Extension\first-python-rag`:

1.  **Project Structure:** Create a new folder structure:
    * `src/parser`
    * `src/embedding`
    * `src/database`
    * `data/` (for database storage)
2.  **Virtual Environment:** Create a python virtual environment named `venv`.
3.  **Dependencies:** Create a `requirements.txt` with the following packages:
    * `tree-sitter`
    * `tree-sitter-java`
    * `lancedb`
    * `sentence-transformers` (or `transformers` + `torch` for Jina V3)
    * `einops` (required for Jina V3)
    * `openai` (for the LLM enrichment step)
    * `tqdm` (for progress bars)
4.  **Verification Script:** Create a script named `verify_setup.py`.
    * It must check if the path `C:\models\huggingface\JinaV3\jina-embeddings-v3` exists.
    * It should try to load the model from that local path using HuggingFace `AutoModel` to ensure it works.
    * If it fails, print a clear error message.

Execute the setup and install the requirements.

```

---

### **Step 2: The AST Parser (Structural Chunking)**

**Goal:** Implement the logic to parse Java files using Tree-sitter. We need to extract methods *with* their class context (fields), not just the method text.

**Prompt for Antigravity:**

```markdown
I need to implement the parsing logic using `tree-sitter` for Java.
**Constraint:** Do NOT use standard text splitters. Code must be parsed structurally.

Create a file `src/parser/java_parser.py` with a class `JavaCodeParser`.
1.  **Initialize:** Load the `tree-sitter-java` grammar.
2.  **Logic:** Implement a method `parse_file(file_path)` that does the following:
    * Reads the .java file.
    * Identifies the **Class Name**.
    * Extracts all **Field Definitions** (e.g., `private int counter;`) to use as context.
    * Extracts all **Method Definitions**.
3.  **Filtering:**
    * Only extract methods that include the `public` modifier.
    * Ignore empty methods or constructors if possible.
4.  **Output:** The method should return a list of dictionaries. Each dictionary must contain:
    * `method_name`: The name of the method.
    * `method_signature`: The full signature (e.g., `public void test(int x)`).
    * `method_body`: The actual code block.
    * `class_context`: A string combining the Class Name and its Fields (e.g., "Class: Bot, Fields: private Widget w").

Create a test script `test_parser.py` that runs this parser on one specific Java file from `E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot` to verify the output format.

```

---

### **Step 3: The Enrichment Layer (Synthetic Documentation)**

**Goal:** Create the "Enricher" that sends code to an LLM to generate summaries. This solves the "vocabulary mismatch" problem.

**Prompt for Antigravity:**

```markdown
I need to implement the "Enrichment" step where we generate summaries for our code chunks.

Create a file `src/embedding/enricher.py`.
1.  Define a class `CodeEnricher`.
2.  It should have an `async` method `enrich_batch(chunks)` that takes a list of code chunks (from Step 2).
3.  **LLM Interaction:**
    * Use an OpenAI-compatible client (or a mock if API key is not set for now).
    * Construct a prompt for each chunk:
        "System: You are a Java Expert.
         Context: {class_context}
         Code: {method_body}
         Task: Summarize the business logic in 1 sentence and provide 3-5 search keywords. Output JSON."
4.  **Response Handling:** Parse the JSON response and attach `summary` and `keywords` to the chunk object.
5.  **Output:** Return the list of enriched chunks.

*Self-Correction:* Ensure the prompt handling is robust against JSON parsing errors from the LLM.

```

---

### **Step 4: Vector Database & Embedding (LanceDB + Jina)**

**Goal:** Set up LanceDB and the Jina embedding logic. We need to embed the *Virtual Document* (Summary + Signature), not just the raw code.

**Prompt for Antigravity:**

```markdown
I need to set up the Vector Database using LanceDB and the local Jina V3 model.

Create a file `src/database/vector_store.py`.
1.  **Model Loading:** Initialize the Jina V3 model from `C:\models\huggingface\JinaV3\jina-embeddings-v3` using the `trust_remote_code=True` flag if required by Jina.
2.  **Schema Design:** Define a PyArrow schema or LanceDB Pydantic model with these fields:
    * `id`: String (Unique ID, e.g., ClassName.MethodName)
    * `vector`: The embedding vector (check Jina V3 dimension, likely 1024).
    * `code`: String (The raw code to display later).
    * `metadata`: String (JSON string of signature, path, class context).
    * `search_text`: String (The "Virtual Document" we used for embedding).
3.  **Embedding Logic:** Create a method `embed_texts(texts)` that passes the text through the Jina model.
    * *Critical:* Jina V3 requires specific task instructions. Ensure you prefix the input with the task: "passage: " or use the specific Jina V3 API `model.encode(..., task="retrieval.passage")`.
4.  **Upsert:** Implement an `add_batch` method to insert data into LanceDB.

Create a `test_db.py` to verify you can embed a simple string "hello world" and save it to LanceDB.

```

---

### **Step 5: The Ingestion Pipeline (Putting it together)**

**Goal:** Create the main script that walks the directory, parses, enriches, and saves data.

**Prompt for Antigravity:**

```markdown
Now we need to combine all components into a streaming ingestion pipeline.

Create `main_ingest.py`.
1.  **File Walker:** Recursively walk through `E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot` and find all `.java` files.
2.  **Batching Logic:**
    * Initialize `JavaCodeParser`, `CodeEnricher`, and `VectorStore`.
    * Create a buffer list.
    * Loop through files, parse them, and add chunks to the buffer.
    * When `len(buffer) >= 20`:
        a. Call `enricher.enrich_batch(buffer)`.
        b. Construct the "Virtual Document" for embedding: `f"Summary: {summary} | Keywords: {keywords} | Signature: {signature}"`.
        c. Generate embeddings using `vector_store`.
        d. Save to LanceDB.
        e. Clear buffer.
3.  **Progress Tracking:** Use `tqdm` to show progress.

*Constraint:* Ensure the script handles exceptions (e.g., if a file fails to parse) without crashing the whole pipeline. Log errors to `ingestion_errors.log`.

```

---

### **Step 6: The Retrieval System (RAG Search)**

**Goal:** A simple interface to query the database.

**Prompt for Antigravity:**

```markdown
Finally, create a search interface `search.py`.

1.  **Input:** Accept a user query string (e.g., "How do I click a widget?").
2.  **Query Expansion (Optional but recommended):** Use the LLM to expand the query into 2-3 variations.
3.  **Embedding:** Embed the query using Jina V3.
    * *Critical:* Use the query-specific task prefix for Jina: `task="retrieval.query"`.
4.  **Search:** Query LanceDB for the top 5 nearest neighbors.
5.  **Display:** Print the results nicely:
    * **Score:** The similarity score.
    * **Summary:** The LLM-generated summary (from metadata).
    * **Code:** The actual code snippet.
    * **File Path:** Where this code lives.

```