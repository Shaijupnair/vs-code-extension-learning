"""
Test Ollama enrichment quality with real MAT project code.
Verifies that DeepSeek Coder produces good summaries despite occasional JSON errors.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from embedding.enricher import CodeEnricher


# Real code samples from MAT project
REAL_SAMPLES = [
    {
        'method_name': 'equals',
        'method_signature': 'public boolean equals(Object obj)',
        'method_body': '''public boolean equals(Object obj) {
    if (this == obj)
        return true;
    if (obj == null)
        return false;
    if (getClass() != obj.getClass())
        return false;
    PackageSpecification other = (PackageSpecification) obj;
    if (isModule != other.isModule)
        return false;
    if (name == null) {
        if (other.name != null)
            return false;
    } else if (!name.equals(other.name))
        return false;
    if (classLoader != other.classLoader)
        return false;
    return true;
}''',
        'class_context': 'Package: org.mat, Class: PackageSpecification',
        'dependency_types': ['Object']
    },
    {
        'method_name': 'compare',
        'method_signature': 'public int compare(IClass c1, IClass c2)',
        'method_body': '''public int compare(IClass c1, IClass c2) {
    long v1 = c1.getRetainedHeapSize();
    long v2 = c2.getRetainedHeapSize();
    return v1 > v2 ? -1 : (v1 == v2 ? 0 : 1);
}''',
        'class_context': 'Package: org.mat.snapshot, Class: RetainedSizeComparator',
        'dependency_types': ['IClass']
    },
    {
        'method_name': 'parseDate',
        'method_signature': 'private long parseDate(String value)',
        'method_body': '''private long parseDate(String value) throws SnapshotException {
    try {
        return Long.parseLong(value);
    } catch (NumberFormatException e) {
        try {
            return DateFormat.getDateTimeInstance().parse(value).getTime();
        } catch (ParseException e2) {
            throw new SnapshotException("Unable to parse date: " + value, e2);
        }
    }
}''',
        'class_context': 'Package: org.mat.parser, Class: HprofParser',
        'dependency_types': ['String', 'SnapshotException', 'DateFormat']
    }
]


async def test_ollama_enrichment():
    """Test Ollama enrichment with real code samples."""
    
    print("=" * 100)
    print("Testing Ollama Enrichment Quality")
    print("=" * 100)
    print("\nUsing DeepSeek Coder via Ollama")
    print("Testing with real MAT project code samples\n")
    
    # Initialize enricher with Ollama
    enricher = CodeEnricher(
        provider="ollama",
        model="deepseek-coder",
        ollama_base_url="http://localhost:11434"
    )
    
    if enricher.mock_mode:
        print("❌ ERROR: Ollama not connected!")
        print("Make sure Ollama is running: ollama serve")
        return
    
    print("✓ Connected to Ollama\n")
    print("-" * 100)
    
    # Enrich samples
    print(f"\nEnriching {len(REAL_SAMPLES)} real code samples...\n")
    enriched = await enricher.enrich_batch(REAL_SAMPLES)
    
    # Display results
    success_count = 0
    fallback_count = 0
    
    for i, (original, result) in enumerate(zip(REAL_SAMPLES, enriched), 1):
        print(f"\n{'='*100}")
        print(f"Sample {i}/{len(REAL_SAMPLES)}: {original['method_name']}")
        print(f"{'='*100}")
        
        print(f"\n📋 Original Code:")
        print(f"   Signature: {original['method_signature']}")
        print(f"   Lines: {len(original['method_body'].split(chr(10)))}")
        
        summary = result.get('summary', '')
        keywords = result.get('keywords', [])
        
        # Check if fallback was used
        is_fallback = 'enrichment failed' in summary.lower() or 'enrichment unavailable' in summary.lower()
        
        if is_fallback:
            print(f"\n⚠️  Fallback Enrichment Used (JSON parsing failed)")
            fallback_count += 1
        else:
            print(f"\n✅ Enrichment Successful")
            success_count += 1
        
        print(f"\n📝 Generated Summary:")
        print(f"   {summary}")
        
        print(f"\n🏷️  Generated Keywords:")
        print(f"   {', '.join(keywords) if keywords else 'None'}")
        
        # Quality assessment
        print(f"\n🔍 Quality Check:")
        if is_fallback:
            print("   ⚠️  Status: Fallback (chunk still indexed)")
            print("   ℹ️  Note: Method name and basic info still searchable")
        else:
            # Check if summary is meaningful
            has_method_name = original['method_name'].lower() in summary.lower()
            has_keywords = len(keywords) >= 3
            summary_length = len(summary.split())
            
            quality_score = 0
            if has_method_name: quality_score += 1
            if has_keywords: quality_score += 1
            if 10 <= summary_length <= 50: quality_score += 1
            
            print(f"   ✓ Method referenced: {has_method_name}")
            print(f"   ✓ Keywords count: {len(keywords)} (target: 3-5)")
            print(f"   ✓ Summary length: {summary_length} words (target: 10-50)")
            print(f"   ⭐ Quality Score: {quality_score}/3")
    
    # Overall statistics
    print(f"\n\n{'='*100}")
    print("OVERALL RESULTS")
    print(f"{'='*100}")
    print(f"\n✅ Successful Enrichments: {success_count}/{len(enriched)} ({success_count/len(enriched)*100:.1f}%)")
    print(f"⚠️  Fallback Used: {fallback_count}/{len(enriched)} ({fallback_count/len(enriched)*100:.1f}%)")
    
    print(f"\n📊 Assessment:")
    success_rate = success_count / len(enriched) * 100
    
    if success_rate >= 80:
        print(f"   🌟 EXCELLENT: {success_rate:.1f}% success rate")
        print(f"   ➜ Ollama enrichment is working very well!")
    elif success_rate >= 50:
        print(f"   ✅ GOOD: {success_rate:.1f}% success rate")
        print(f"   ➜ Ollama enrichment is working adequately")
        print(f"   ℹ️  Note: Fallback chunks are still searchable by method name")
    else:
        print(f"   ⚠️  LOW: {success_rate:.1f}% success rate")
        print(f"   ➜ Consider using OpenAI for better JSON compliance")
    
    print(f"\n💡 Key Insight:")
    print(f"   Even with {fallback_count} fallback(s), ALL chunks get indexed and are searchable.")
    print(f"   Fallback provides: method name + 'enrichment-failed' keyword + basic info")
    print(f"   This ensures no code is lost, just less semantic enrichment for failed chunks.")
    
    print(f"\n{'='*100}\n")


if __name__ == "__main__":
    asyncio.run(test_ollama_enrichment())
