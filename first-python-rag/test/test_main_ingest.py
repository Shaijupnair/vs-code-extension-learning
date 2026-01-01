"""
Test the main ingestion pipeline with a small subset.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import after path setup
sys.path.insert(0, str(Path(__file__).parent.parent))
from main_ingest import IngestionPipeline


async def test_pipeline():
    """Test pipeline with test files."""
    print("=" * 80)
    print("Testing Ingestion Pipeline")
    print("=" * 80)
    
    # Test with our test files
    test_root = Path(__file__).parent / "dependency_test"
    
    print(f"\nTest directory: {test_root}")
    print("This directory contains:")
    print("  - Transaction.java (3 constructors)")
    print("  - Widget.java (2 constructors)")
    print("  - TransactionProcessor.java (dependencies + constructor)")
    
    # Create pipeline
    pipeline = IngestionPipeline(
        root_path=str(test_root),
        batch_size=5,  # Small batch for testing
        db_path="./test/test_ingest_db",
        mock_enrichment=True  # Use mock to avoid API calls
    )
    
    # Run pipeline
    await pipeline.run()
    
    # Verify results
    print("\n" + "=" * 80)
    print("Verification")
    print("=" * 80)
    
    db_stats = pipeline.vector_store.get_stats()
    print(f"\nDatabase contains {db_stats['count']} records")
    
    # Test search
    print("\nTesting search functionality:")
    results = pipeline.vector_store.search("create transaction", limit=3)
    
    print(f"Search for 'create transaction' returned {len(results)} results:")
    for i, result in enumerate(results, 1):
        if 'metadata_parsed' in result:
            meta = result['metadata_parsed']
            print(f"\n  {i}. {meta['method_name']}")
            print(f"     Package: {meta['package']}")
            print(f"     Signature: {meta['signature'][:60]}...")
    
    print("\n" + "=" * 80)
    print("✓ Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_pipeline())
