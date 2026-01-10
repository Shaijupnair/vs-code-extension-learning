"""
Test script to verify Ollama integration is working correctly.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from embedding.enricher import CodeEnricher


async def test_ollama():
    """Test Ollama enrichment with a sample code chunk."""
    
    print("=" * 80)
    print("Testing Ollama Integration")
    print("=" * 80)
    
    # Sample Java code chunk
    sample_chunk = {
        'method_name': 'validateTransaction',
        'method_signature': 'public boolean validateTransaction(Transaction t)',
        'method_body': '''public boolean validateTransaction(Transaction t) {
    if (t == null) {
        return false;
    }
    if (t.getAmount() <= 0) {
        return false;
    }
    if (!t.hasValidUser()) {
        return false;
    }
    return true;
}''',
        'class_context': 'Package: com.example.payment, Class: TransactionValidator',
        'dependency_types': ['Transaction']
    }
    
    # Test 1: Ollama
    print("\n1️⃣ Testing Ollama Provider")
    print("-" * 80)
    try:
        enricher_ollama = CodeEnricher(
            provider="ollama",
            model="deepseek-coder",
            ollama_base_url="http://localhost:11434"
        )
        
        print(f"Provider: ollama")
        print(f"Model: deepseek-coder")
        print(f"Mock mode: {enricher_ollama.mock_mode}")
        
        if enricher_ollama.mock_mode:
            print("\n❌ Ollama not connected - running in mock mode")
            print("Make sure Ollama is running: ollama serve")
        else:
            print("\n✓ Connected to Ollama")
            print("\nEnriching sample chunk...")
            
            enriched = await enricher_ollama.enrich_batch([sample_chunk])
            
            if enriched:
                result = enriched[0]
                print("\n✓ Enrichment successful!")
                print(f"\n📝 Summary:")
                print(f"   {result.get('summary', 'N/A')}")
                print(f"\n🏷️  Keywords:")
                print(f"   {', '.join(result.get('keywords', []))}")
            else:
                print("\n❌ Enrichment failed")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: OpenAI (if API key available)
    print("\n\n2️⃣ Testing OpenAI Provider (for comparison)")
    print("-" * 80)
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv("OPENAI_API_KEY"):
            enricher_openai = CodeEnricher(
                provider="openai",
                model="gpt-4o-mini"
            )
            
            print(f"Provider: openai")
            print(f"Model: gpt-4o-mini")
            print(f"Mock mode: {enricher_openai.mock_mode}")
            
            if not enricher_openai.mock_mode:
                print("\n✓ Connected to OpenAI")
                print("\nEnriching sample chunk...")
                
                enriched = await enricher_openai.enrich_batch([sample_chunk])
                
                if enriched:
                    result = enriched[0]
                    print("\n✓ Enrichment successful!")
                    print(f"\n📝 Summary:")
                    print(f"   {result.get('summary', 'N/A')}")
                    print(f"\n🏷️  Keywords:")
                    print(f"   {', '.join(result.get('keywords', []))}")
        else:
            print("⚠️  No OpenAI API key - skipping")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_ollama())
