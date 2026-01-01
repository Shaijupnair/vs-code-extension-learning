"""
Test context-aware enrichment with inheritance scenario.
Verifies that inherited methods are included in prompts.
"""

import sys
import asyncio
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser.java_parser import JavaCodeParser
from embedding.enricher import CodeEnricher


async def test_context_aware_enrichment():
    """Test enricher with inheritance context (Dog extends Animal)."""
    print("=" * 80)
    print("Testing Context-Aware Enrichment with Inheritance")
    print("=" * 80)
    
    # Step 1: Build hierarchy map for inheritance
    print("\n📊 Step 1: Building Hierarchy Map")
    print("─" * 80)
    
    from parser.hierarchy_scanner import build_project_map
    
    test_dir = Path(__file__).parent / "inheritance_test"
    hierarchy_file = test_dir / "project_hierarchy.json"
    
    # Build hierarchy (if not already exists)
    if not hierarchy_file.exists():
        print("Building hierarchy map...")
        build_project_map(str(test_dir), str(hierarchy_file))
    else:
        print(f"Using existing hierarchy file: {hierarchy_file}")
    
    # Step 2: Parse Dog.java with inheritance context
    print("\n\n📝 Step 2: Parsing Dog.java with Inheritance")
    print("─" * 80)
    
    parser = JavaCodeParser(hierarchy_map_path=str(hierarchy_file))
    dog_file = test_dir / "Dog.java"
    dog_chunks = parser.parse_file(str(dog_file))
    
    print(f"Parsed {len(dog_chunks)} chunks from Dog class")
    
    # Show one chunk to verify inheritance context
    if dog_chunks:
        sample = dog_chunks[0]
        print(f"\nSample chunk: {sample['method_name']}")
        print(f"Class Context: {sample['class_context'][:100]}...")
        
        # Check if inheritance is present
        has_inheritance = 'Inherited Methods' in sample['class_context']
        print(f"✓ Has inherited methods: {has_inheritance}")
    
    # Step 3: Enrich with context-aware prompts
    print("\n\n🤖 Step 3: Enriching with Context-Aware Prompts")
    print("─" * 80)
    print("Using MOCK mode to show prompt structure...")
    
    # Mock mode to avoid API costs, but show prompt
    enricher = CodeEnricher(mock_mode=True)
    
    # Build and display a sample prompt
    if dog_chunks:
        sample_chunk = dog_chunks[0]
        sample_prompt = enricher._build_prompt(sample_chunk)
        
        print("\n📋 Sample Prompt Generated:")
        print("─" * 80)
        print(sample_prompt[:800] + "\n... (truncated for display)")
        print("─" * 80)
        
        # Check prompt includes key elements
        checks = {
            "Package name": "Package:" in sample_prompt,
            "Class context": "Class Context:" in sample_prompt,
            "Method signature": "Method Signature:" in sample_prompt,
            "Dependencies": "Dependencies:" in sample_prompt,
            "Inherited methods": "Inherited Methods" in sample_prompt if has_inheritance else True,
            "Business logic focus": "BUSINESS LOGIC" in sample_prompt
        }
        
        print("\n✅ Prompt Quality Checks:")
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
    
    # Step 4: Enrich chunks
    print("\n\n🔄 Step 4: Running Enrichment")
    print("─" * 80)
    
    enriched_chunks = await enricher.enrich_batch(dog_chunks)
    
    print(f"Enriched {len(enriched_chunks)} chunks")
    
    # Display results
    print("\n\n📊 Step 5: Enrichment Results")
    print("=" * 80)
    
    for i, chunk in enumerate(enriched_chunks[:3], 1):
        print(f"\n{i}. {chunk['method_name']}")
        print(f"   Signature: {chunk['method_signature'][:70]}...")
        print(f"   Summary: {chunk.get('summary', 'N/A')}")
        print(f"   Keywords: {chunk.get('keywords', [])}")
        
        # Show context includes inheritance
        if 'Inherited Methods' in chunk['class_context']:
            print(f"   ✓ Includes inherited methods from Animal")
    
    # Save results
    output_file = test_dir / "context_aware_enrichment.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_chunks, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    # Step 6: Test with real API (optional, commented out)
    print("\n\n💡 Optional: Test with Real API")
    print("=" * 80)
    print("To test with real OpenAI API, uncomment the code below and run:")
    print("""
# enricher_real = CodeEnricher(mock_mode=False, model='gpt-4o-mini')
# enriched_real = await enricher_real.enrich_batch(dog_chunks[:2])
# for chunk in enriched_real:
#     print(f"{chunk['method_name']}: {chunk['summary']}")
""")
    
    print("\n" + "=" * 80)
    print("🎉 Context-Aware Enrichment Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_context_aware_enrichment())
