"""
Test enricher with real OpenAI API.
"""

import sys
import asyncio
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser.java_parser import JavaCodeParser
from embedding.enricher import CodeEnricher


async def test_real_api():
    """Test with real OpenAI API."""
    print("=" * 80)
    print("Testing Code Enrichment with Real OpenAI API")
    print("=" * 80)
    
    # Parse a small Java file
    print("\n📝 Step 1: Parsing Java Code")
    print("─" * 80)
    
    test_file = Path(__file__).parent / "dependency_test" / "Widget.java"
    parser = JavaCodeParser()
    chunks = parser.parse_file(str(test_file))
    
    print(f"Parsed {len(chunks)} code chunks from Widget.java")
    for i, chunk in enumerate(chunks, 1):
        print(f"  {i}. {chunk['method_name']}: {chunk['method_signature'][:60]}...")
    
    # Limit to 3 chunks to save API costs
    chunks_to_enrich = chunks[:3]
    print(f"\nWill enrich {len(chunks_to_enrich)} chunks (to save costs)")
    
    # Enrich with real API
    print("\n\n🤖 Step 2: Enriching with OpenAI API")
    print("─" * 80)
    print("Calling OpenAI API (gpt-4o-mini)...")
    
    enricher = CodeEnricher(mock_mode=False, model='gpt-4o-mini')
    enriched_chunks = await enricher.enrich_batch(chunks_to_enrich)
    
    # Display results
    print("\n\n📊 Step 3: Real API Results")
    print("=" * 80)
    
    for i, chunk in enumerate(enriched_chunks, 1):
        print(f"\n{i}. {chunk['method_name']}")
        print(f"   Signature: {chunk['method_signature']}")
        print(f"   Summary: {chunk.get('summary', 'N/A')}")
        print(f"   Keywords: {chunk.get('keywords', [])}")
    
    # Save results
    output_file = Path(__file__).parent / "real_api_enrichment.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_chunks, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ Real API Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_real_api())
