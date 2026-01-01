# Quick Start: Inheritance Context Usage

## Overview

The inheritance context feature enriches parsed Java methods with information about inherited methods from parent classes.

## Two-Step Process

### Step 1: Build Project Hierarchy Map

Run this **once** (or when codebase structure changes):

```python
from src.parser.hierarchy_scanner import build_project_map

# Build hierarchy for your Java project
hierarchy_map = build_project_map(
    root_path="/path/to/java/project",
    output_file="project_hierarchy.json"  # Will be saved in root_path
)
```

**Output:** `project_hierarchy.json` file containing inheritance tree.

### Step 2: Parse with Inheritance Context

```python
from src.parser.java_parser import JavaCodeParser

# Initialize parser WITH hierarchy map
parser = JavaCodeParser(hierarchy_map_path="project_hierarchy.json")

# Parse files
results = parser.parse_file("path/to/Dog.java")

# Check class context
for method in results:
    print(method['class_context'])
    # Now includes: Extends: Animal, Inherited Methods: [eat, sleep, ...]
```

## What You Get

### Without Inheritance Context:
```json
{
  "class_context": "Package: com.example, Class: Dog, Fields: private String breed;"
}
```

### With Inheritance Context:
```json
{
  "class_context": "Package: com.example, Class: Dog, Fields: private String breed;, Extends: Animal, Inherited Methods: [eat, sleep, getName, makeSound]"
}
```

## Key Features

✅ **Recursive Inheritance** - Handles grandparents, great-grandparents, etc.  
✅ **External Library Safe** - Gracefully ignores classes not in your codebase  
✅ **Backward Compatible** - Works without hierarchy map (just omit parameter)  
✅ **Fast** - JSON loaded once, O(1) lookups

## Command-Line Usage

Build hierarchy from terminal:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run hierarchy scanner
python src/parser/hierarchy_scanner.py E:\path\to\java\project
```

## Testing

Run the test to verify:

```bash
.\venv\Scripts\Activate.ps1
python test\test_inheritance.py
```

## Example: Real Project

```python
# For SWTBot project
from src.parser.hierarchy_scanner import build_project_map
from src.parser.java_parser import JavaCodeParser

# Step 1: Build hierarchy (one time)
build_project_map(
    root_path="E:\\OpenSource\\eclipse\\swtbot\\org.eclipse.swtbot",
    output_file="E:\\Learn_Vs_Code_Extension\\first-python-rag\\data\\swtbot_hierarchy.json"
)

# Step 2: Parse with context
parser = JavaCodeParser(
    hierarchy_map_path="E:\\Learn_Vs_Code_Extension\\first-python-rag\\data\\swtbot_hierarchy.json"
)

results = parser.parse_file("path/to/SomeClass.java")
```

## Notes

- **Hierarchy map** should be rebuilt when class structure changes
- **Parser** can be reused for multiple files (hierarchy loaded once)
- **Missing parents** (e.g., `ArrayList`, Eclipse libs) are safely ignored
- **Simple names** work even if packages differ

---

Happy parsing with full inheritance context! 🎉
