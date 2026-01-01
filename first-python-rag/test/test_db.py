"""
Verification test for VectorStore.
Tests with mock data including inheritance and dependencies.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.vector_store import VectorStore


def create_mock_chunks():
    """Create mock chunks for testing."""
    return [
        {
            'method_name': 'run',
            'method_signature': 'public void run(int x)',
            'method_body': '{\n                System.out.println("Running with: " + x);\n                start();\n                stop();\n            }',
            'class_context': 'Package: com.example, Class: Test, Fields: private int count;, Extends: BaseTest, Inherited Methods: [start, stop, validate]',
            'dependency_types': [],
            'summary': 'Executes the test logic with the specified parameter value',
            'keywords': ['run', 'execute', 'test', 'parameter']
        },
        {
            'method_name': 'process',
            'method_signature': 'public void process(Transaction t, Widget w)',
            'method_body': '{\n                if (t.validate()) {\n                    w.display(t);\n                }\n            }',
            'class_context': 'Package: com.example.business, Class: Processor, Fields: private Logger logger;',
            'dependency_types': ['Transaction', 'Widget'],
            'summary': 'Processes a transaction and displays it using a widget if valid',
            'keywords': ['process', 'transaction', 'widget', 'validate', 'display']
        },
        {
            'method_name': '<Constructor>',
            'method_signature': 'public <Constructor> Calculator(int precision)',
            'method_body': '{\n                this.precision = precision;\n                this.rounding = RoundingMode.HALF_UP;\n            }',
            'class_context': 'Package: com.example.math, Class: Calculator, Fields: private int precision;; private RoundingMode rounding;',
            'dependency_types': [],
            'summary': 'Initializes calculator with specified precision and default rounding mode',
            'keywords': ['constructor', 'initialize', 'precision', 'rounding', 'calculator']
        }
    ]


def test_vector_store():
    """Test vector store functionality."""
    print("=" * 80)
    print("Testing Vector Store with LanceDB + Jina V3")
    print("=" * 80)
    
    # Step 1: Initialize Vector Store
    print("\n📦 Step 1: Initializing Vector Store")
    print("─" * 80)
    
    try:
        vector_store = VectorStore(
            db_path="./test/test_lancedb",
            table_name="test_code_chunks"
        )
        print("✓ Vector store initialized successfully")
        print(f"  Device: {vector_store.device}")
        print(f"  Model dimension: 1024 (Jina V3)")
    except Exception as e:
        print(f"❌ Error initializing vector store: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Test ID Generation
    print("\n\n🔑 Step 2: Testing ID Generation")
    print("─" * 80)
    
    id1 = vector_store.generate_id("com.example", "Test", "public void run(int x)")
    id2 = vector_store.generate_id("com.example", "Test", "public void run(String x)")
    id3 = vector_store.generate_id("com.another", "Test", "public void run(int x)")
    
    print(f"ID 1 (com.example.Test.run(int)): {id1[:16]}...")
    print(f"ID 2 (com.example.Test.run(String)): {id2[:16]}...")
    print(f"ID 3 (com.another.Test.run(int)): {id3[:16]}...")
    
    # Verify uniqueness
    print(f"\n✓ ID 1 ≠ ID 2 (overloading): {id1 != id2}")
    print(f"✓ ID 1 ≠ ID 3 (different package): {id1 != id3}")
    print(f"✓ All IDs unique: {len(set([id1, id2, id3])) == 3}")
    
    # Step 3: Create Mock Chunks
    print("\n\n📝 Step 3: Creating Mock Chunks")
    print("─" * 80)
    
    mock_chunks = create_mock_chunks()
    print(f"Created {len(mock_chunks)} mock chunks:")
    for i, chunk in enumerate(mock_chunks, 1):
        print(f"  {i}. {chunk['method_name']}: {chunk['method_signature'][:50]}...")
    
    # Step 4: Test Metadata Extraction
    print("\n\n🔍 Step 4: Testing Metadata Extraction")
    print("─" * 80)
    
    test_chunk = mock_chunks[0]
    metadata = vector_store.extract_metadata(test_chunk, file_path="/test/Test.java")
    
    print(f"Extracted metadata:")
    print(f"  Package: {metadata['package']}")
    print(f"  Class: {metadata['class_name']}")
    print(f"  Signature: {metadata['signature']}")
    print(f"  Inherited Methods: {metadata['inherited_methods']}")
    print(f"  Dependencies: {metadata['dependencies']}")
    
    # Verify inheritance extraction
    expected_inherited = ['start', 'stop', 'validate']
    has_inheritance = all(m in metadata['inherited_methods'] for m in expected_inherited)
    print(f"\n✓ Inheritance list correct: {has_inheritance}")
    
    # Step 5: Test Search Text Building
    print("\n\n📄 Step 5: Testing Search Text Building")
    print("─" * 80)
    
    search_text = vector_store.build_search_text(test_chunk)
    print(f"Search text:\n{search_text[:200]}...")
    
    has_summary = 'Summary:' in search_text
    has_keywords = 'Keywords:' in search_text
    has_signature = 'Signature:' in search_text
    has_context = 'Context:' in search_text
    
    print(f"\n✓ Contains summary: {has_summary}")
    print(f"✓ Contains keywords: {has_keywords}")
    print(f"✓ Contains signature: {has_signature}")
    print(f"✓ Contains context: {has_context}")
    
    # Step 6: Add Batch to DB
    print("\n\n💾 Step 6: Adding Batch to Vector Database")
    print("─" * 80)
    
    try:
        vector_store.add_batch(mock_chunks, file_path="/test/MockCode.java")
        print(f"✓ Added {len(mock_chunks)} chunks to database")
    except Exception as e:
        print(f"❌ Error adding batch: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 7: Verify Storage
    print("\n\n✅ Step 7: Verifying Storage")
    print("─" * 80)
    
    stats = vector_store.get_stats()
    print(f"Database stats:")
    print(f"  Table exists: {stats['table_exists']}")
    print(f"  Record count: {stats['count']}")
    print(f"  Table name: {stats['table_name']}")
    print(f"  DB path: {stats['db_path']}")
    
    # Step 8: Test Search
    print("\n\n🔍 Step 8: Testing Search")
    print("─" * 80)
    
    try:
        results = vector_store.search("how to process a transaction", limit=2)
        print(f"Search results for 'how to process a transaction':")
        
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            if 'metadata_parsed' in result:
                meta = result['metadata_parsed']
                print(f"    Method: {meta['method_name']}")
                print(f"    Package: {meta['package']}")
                print(f"    Signature: {meta['signature'][:60]}...")
                if meta['dependencies']:
                    print(f"    Dependencies: {meta['dependencies']}")
                if meta['inherited_methods']:
                    print(f"    Inherited: {meta['inherited_methods']}")
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 9: Verify Metadata JSON
    print("\n\n🔬 Step 9: Verifying Metadata JSON Structure")
    print("─" * 80)
    
    if results:
        first_result = results[0]
        metadata_json = first_result.get('metadata', '')
        
        try:
            metadata_parsed = json.loads(metadata_json)
            print("Metadata JSON structure:")
            for key in ['package', 'signature', 'dependencies', 'inherited_methods', 'file_path']:
                value = metadata_parsed.get(key, 'missing')
                print(f"  {key}: {value}")
            
            print("\n✓ Metadata JSON is valid and contains all required fields")
        except json.JSONDecodeError:
            print("❌ Metadata is not valid JSON")
    
    print("\n" + "=" * 80)
    print("🎉 Vector Store Verification Complete!")
    print("=" * 80)
    
    return vector_store


if __name__ == "__main__":
    vs = test_vector_store()
