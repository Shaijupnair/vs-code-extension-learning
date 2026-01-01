"""
Test script for code enrichment module.
"""

import sys
import asyncio
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser.java_parser import JavaCodeParser
from embedding.enricher import CodeEnricher


async def test_enrichment():
    """Test code enrichment with mock mode."""
    print("=" * 80)
    print("Testing Code Enrichment")
    print("=" * 80)
    
    # Step 1: Parse some Java code to get chunks
    print("\n📝 STEP 1: Parsing Java Code")
    print("─" * 80)
    
    test_file = Path(__file__).parent / "dependency_test" / "TransactionProcessor.java"
    parser = JavaCodeParser()
    chunks = parser.parse_file(str(test_file))
    
    print(f"Parsed {len(chunks)} code chunks")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"{i}. {chunk['method_name']}: {chunk['method_signature'][:60]}...")
    
    # Step 2: Enrich chunks (mock mode - no API key needed)
    print("\n\n🤖 STEP 2: Enriching with Mock LLM")
    print("─" * 80)
    print("Running in MOCK MODE (no API calls)")
    
    enricher = CodeEnricher(mock_mode=True, max_concurrent=3)
    enriched_chunks = await enricher.enrich_batch(chunks)
    
    print(f"\nEnriched {len(enriched_chunks)} chunks")
    
    # Step 3: Display enriched results
    print("\n\n📊 STEP 3: Enrichment Results")
    print("=" * 80)
    
    for i, chunk in enumerate(enriched_chunks[:5], 1):
        print(f"\n{i}. {chunk['method_name']}")
        print(f"   Signature: {chunk['method_signature'][:70]}...")
        print(f"   Summary: {chunk.get('summary', 'N/A')}")
        print(f"   Keywords: {chunk.get('keywords', [])}")
        if chunk.get('dependency_types'):
            print(f"   Dependencies: {chunk['dependency_types']}")
    
    # Step 4: Verify all chunks have enrichment
    print("\n\n✅ STEP 4: Verification")
    print("=" * 80)
    
    has_summary = all('summary' in c for c in enriched_chunks)
    has_keywords = all('keywords' in c for c in enriched_chunks)
    
    print(f"All chunks have summary: {has_summary}")
    print(f"All chunks have keywords: {has_keywords}")
    
    # Count constructors
    constructors = [c for c in enriched_chunks if c['method_name'] == '<Constructor>']
    methods = [c for c in enriched_chunks if c['method_name'] != '<Constructor>']
    
    print(f"Constructors enriched: {len(constructors)}")
    print(f"Methods enriched: {len(methods)}")
    
    # Save enriched chunks
    output_file = Path(__file__).parent / "enriched_chunks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_chunks, f, indent=2)
    
    print(f"\n📄 Enriched chunks saved to: {output_file}")
    
    # Step 5: Show how to use with real API
    print("\n\n💡 STEP 5: Using with Real OpenAI API")
    print("=" * 80)
    print("""
To use with real OpenAI API:

import os
os.environ['OPENAI_API_KEY'] = 'your-api-key'

enricher = CodeEnricher(mock_mode=False, model='gpt-4o-mini')
enriched = await enricher.enrich_batch(chunks)

# Or use environment variable:
export OPENAI_API_KEY='your-api-key'
enricher = CodeEnricher()  # Will auto-detect API key
""")
    
    print("\n" + "=" * 80)
    print("🎉 Enrichment Testing Complete!")
    print("=" * 80)


async def test_with_real_api_if_available():
    """Test with real API if key is available."""
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("\n⚠️  No OPENAI_API_KEY found - skipping real API test")
        return
    
    print("\n" + "=" * 80)
    print("Testing with Real OpenAI API")
    print("=" * 80)
    
    # Parse a small sample
    test_file = Path(__file__).parent / "dependency_test" / "Widget.java"
    parser = JavaCodeParser()
    chunks = parser.parse_file(str(test_file))
    
    print(f"\nParsed {len(chunks)} chunks from Widget.java")
    
    # Enrich with real API (limit to 3 chunks to save costs)
    chunks_to_enrich = chunks[:3]
    print(f"Enriching {len(chunks_to_enrich)} chunks with real API...")
    
    enricher = CodeEnricher(mock_mode=False, model='gpt-4o-mini')
    enriched = await enricher.enrich_batch(chunks_to_enrich)
    
    print(f"\nReal API Enrichment Results:")
    for chunk in enriched:
        print(f"\n  {chunk['method_name']}:")
        print(f"    Summary: {chunk.get('summary', 'N/A')}")
        print(f"    Keywords: {chunk.get('keywords', [])}")
    
    print("\n✅ Real API test complete!")


if __name__ == "__main__":
    # Run mock test
    asyncio.run(test_enrichment())
    
    # Optionally test with real API
    # asyncio.run(test_with_real_api_if_available())
