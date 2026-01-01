"""
Test the search interface.
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from search import CodeSearchEngine


async def test_search():
    """Test search with pre-indexed data."""
    print("=" * 80)
    print("Testing Search Interface")
    print("=" * 80)
    
    # Initialize search engine (using test database)
    search_engine = CodeSearchEngine(
        db_path="./test/test_ingest_db",
        use_query_expansion=False  # Disable for quick test
    )
    
    # Test queries
    test_queries = [
        "create transaction",
        "widget",
        "constructor"
    ]
    
    for query in test_queries:
        print(f"\n{'='* 80}")
        print(f"Testing Query: \"{query}\"")
        print("=" * 80)
        
        results = await search_engine.search(query, limit=3, expand=False)
        
        if results:
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(search_engine.format_result(result, i))
        else:
            print("No results found")
    
    print("\n" + "=" * 80)
    print("✓ Search Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_search())
