"""
Quick verification script to check if .env file is loaded correctly.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 60)
print("Checking .env Configuration")
print("=" * 60)

# Check if API key is loaded
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    # Show only first and last 4 characters for security
    masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
    print(f"\n✅ OPENAI_API_KEY found: {masked_key}")
    print(f"   Length: {len(api_key)} characters")
    
    # Validate format (OpenAI keys usually start with 'sk-')
    if api_key.startswith('sk-'):
        print("   Format: Valid (starts with 'sk-')")
    else:
        print("   ⚠️  Warning: Key doesn't start with 'sk-' (expected format)")
    
    print("\n✅ .env file is loaded correctly!")
    print("   The enricher will use this API key automatically.")
else:
    print("\n❌ OPENAI_API_KEY not found!")
    print("   Please check your .env file:")
    print("   1. Make sure .env file exists in project root")
    print("   2. Add: OPENAI_API_KEY=your-key-here")
    print("   3. Replace 'your-key-here' with actual API key")

print("\n" + "=" * 60)
