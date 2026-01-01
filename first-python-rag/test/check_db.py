"""
Quick script to check database health and contents.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.vector_store import VectorStore


def check_database():
    """Check database stats and sample data."""
    print("=" * 80)
    print("Database Health Check")
    print("=" * 80)
    
    # Initialize vector store
    print("\n1️⃣ Connecting to database...")
    try:
        vector_store = VectorStore(db_path="./data/lancedb")
        print("✓ Connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Get stats
    print("\n2️⃣ Getting database statistics...")
    stats = vector_store.get_stats()
    
    print(f"\n📊 Database Stats:")
    print(f"   Table exists: {stats['table_exists']}")
    print(f"   Record count: {stats['count']}")
    if 'db_path' in stats:
        print(f"   Database path: {stats['db_path']}")
    
    if stats['count'] == 0:
        print("\n⚠️  Database is empty! Ingestion may not have completed.")
        print("   Run: python main_ingest.py")
        return
    
    # Test search
    print(f"\n3️⃣ Testing search functionality...")
    try:
        results = vector_store.search("click button widget", limit=3)
        print(f"✓ Search returned {len(results)} results")
        
        if results:
            print(f"\n📋 Sample Result:")
            result = results[0]
            
            # Parse metadata
            import json
            if 'metadata' in result:
                meta = json.loads(result['metadata'])
                print(f"   Method: {meta.get('method_name', 'N/A')}")
                print(f"   Package: {meta.get('package', 'N/A')}")
                print(f"   Signature: {meta.get('signature', 'N/A')[:60]}...")
                print(f"   File: {meta.get('file_path', 'N/A')}")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ Database Check Complete")
    print("=" * 80)
    
    if stats['count'] > 0:
        print(f"\n✓ Database is healthy with {stats['count']} code chunks")
        print("✓ Ready to use with search.py")
    else:
        print("\n⚠️  Database needs to be populated")


if __name__ == "__main__":
    check_database()
