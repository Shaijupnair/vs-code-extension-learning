"""
Test enricher on real SWTBot codebase with actual OpenAI API.
Verifies quality of semantic summaries and keywords.
"""

import sys
import asyncio
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser.java_parser import JavaCodeParser
from embedding.enricher import CodeEnricher


async def test_swtbot_enrichment():
    """Test enricher on actual SWTBot code."""
    print("=" * 80)
    print("Testing Enricher on SWTBot Codebase")
    print("=" * 80)
    
    # Step 1: Parse SWTWorkbenchBot.java (real codebase)
    print("\n📝 Step 1: Parsing SWTWorkbenchBot.java")
    print("─" * 80)
    
    swtbot_file = Path("E:/OpenSource/eclipse/swtbot/org.eclipse.swtbot/org.eclipse.swtbot.eclipse.finder/src/org/eclipse/swtbot/eclipse/finder/SWTWorkbenchBot.java")
    
    if not swtbot_file.exists():
        print(f"❌ File not found: {swtbot_file}")
        print("Please update the path to your SWTBot installation")
        return
    
    parser = JavaCodeParser()
    chunks = parser.parse_file(str(swtbot_file))
    
    print(f"\nParsed {len(chunks)} public methods from SWTWorkbenchBot")
    
    # Show sample chunks
    print("\nSample methods:")
    for i, chunk in enumerate(chunks[:5], 1):
        print(f"  {i}. {chunk['method_name']}: {chunk['method_signature'][:70]}...")
    
    # Select interesting methods for enrichment
    # Limit to 5 to save API costs
    chunks_to_enrich = chunks[:5]
    
    print(f"\nWill enrich {len(chunks_to_enrich)} methods with real OpenAI API")
    print("(Limited to save costs - you can increase this for full testing)")
    
    # Step 2: Enrich with real API
    print("\n\n🤖 Step 2: Enriching with OpenAI API (gpt-4o-mini)")
    print("─" * 80)
    print("Calling OpenAI API...")
    
    enricher = CodeEnricher(mock_mode=False, model='gpt-4o-mini', max_concurrent=3)
    enriched_chunks = await enricher.enrich_batch(chunks_to_enrich)
    
    print(f"\nEnriched {len(enriched_chunks)} methods successfully")
    
    # Step 3: Display results
    print("\n\n📊 Step 3: Enrichment Results")
    print("=" * 80)
    
    for i, chunk in enumerate(enriched_chunks, 1):
        print(f"\n{'─' * 80}")
        print(f"Method #{i}: {chunk['method_name']}")
        print(f"{'─' * 80}")
        print(f"Signature: {chunk['method_signature']}")
        print(f"\nPackage: {chunk['class_context'].split(',')[0]}")
        
        if chunk.get('dependency_types'):
            print(f"Dependencies: {chunk['dependency_types']}")
        
        print(f"\nSummary: {chunk.get('summary', 'N/A')}")
        print(f"Keywords: {chunk.get('keywords', [])}")
    
    # Step 4: Quality Analysis
    print("\n\n✅ Step 4: Quality Analysis")
    print("=" * 80)
    
    # Check summary quality
    has_summaries = all('summary' in c and c['summary'] for c in enriched_chunks)
    has_keywords = all('keywords' in c and c['keywords'] for c in enriched_chunks)
    
    print(f"All methods have summaries: {has_summaries}")
    print(f"All methods have keywords: {has_keywords}")
    
    # Check for business logic focus (not implementation details)
    implementation_keywords = ['return', 'takes', 'integer', 'string', 'variable']
    business_focused = []
    
    for chunk in enriched_chunks:
        summary = chunk.get('summary', '').lower()
        is_business = not any(keyword in summary for keyword in implementation_keywords)
        business_focused.append(is_business)
    
    business_count = sum(business_focused)
    print(f"Business logic focused summaries: {business_count}/{len(enriched_chunks)}")
    
    # Check keyword diversity
    all_keywords = []
    for chunk in enriched_chunks:
        all_keywords.extend(chunk.get('keywords', []))
    
    unique_keywords = set(all_keywords)
    print(f"Total keywords: {len(all_keywords)}")
    print(f"Unique keywords: {len(unique_keywords)}")
    print(f"Diversity ratio: {len(unique_keywords)/len(all_keywords):.2%}")
    
    # Step 5: Save results
    output_file = Path(__file__).parent / "swtbot_enrichment_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_chunks, f, indent=2)
    
    print(f"\n📄 Full results saved to: {output_file}")
    
    # Step 6: Sample semantic quality
    print("\n\n🔍 Step 6: Semantic Quality Examples")
    print("=" * 80)
    
    if enriched_chunks:
        best_example = enriched_chunks[0]
        print(f"\nMethod: {best_example['method_name']}")
        print(f"Original signature: {best_example['method_signature']}")
        print(f"\nGenerated summary:")
        print(f"  \"{best_example.get('summary', 'N/A')}\"")
        print(f"\nGenerated keywords:")
        print(f"  {best_example.get('keywords', [])}")
        
        # Compare with simple extraction
        method_name = best_example['method_name']
        print(f"\nComparison:")
        print(f"  Simple approach: Just use method name '{method_name}'")
        print(f"  Enriched approach: Semantic summary + domain keywords")
        print(f"  → Better for semantic search!")
    
    print("\n" + "=" * 80)
    print("🎉 SWTBot Enrichment Test Complete!")
    print("=" * 80)
    
    return enriched_chunks


if __name__ == "__main__":
    results = asyncio.run(test_swtbot_enrichment())
