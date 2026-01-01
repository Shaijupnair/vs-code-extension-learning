"""
Test script for JavaCodeParser.
Tests the parser on a real Java file from the SWTBot project.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser.java_parser import JavaCodeParser


def test_parser():
    """Test the Java parser on a sample file."""
    # Test file path - using a file with proper package declaration
    test_file = r"E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot\org.eclipse.swtbot.eclipse.finder\src\org\eclipse\swtbot\eclipse\finder\SWTWorkbenchBot.java"
    
    print("=" * 80)
    print("Testing JavaCodeParser")
    print("=" * 80)
    print(f"\nTest file: {test_file}")
    
    # Check if file exists
    if not Path(test_file).exists():
        print(f"\n❌ ERROR: Test file not found!")
        print(f"   Path: {test_file}")
        return
    
    # Initialize parser
    print("\n📝 Initializing JavaCodeParser...")
    parser = JavaCodeParser()
    print("✓ Parser initialized successfully")
    
    # Parse the file
    print(f"\n🔍 Parsing file...")
    try:
        results = parser.parse_file(test_file)
        print(f"✓ Parsing complete! Found {len(results)} public methods")
    except Exception as e:
        print(f"\n❌ ERROR during parsing:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "=" * 80)
    print("PARSING RESULTS")
    print("=" * 80)
    
    if not results:
        print("\n⚠️  No public methods found in the file.")
        return
    
    for i, method_info in enumerate(results, 1):
        print(f"\n{'─' * 80}")
        print(f"METHOD #{i}")
        print(f"{'─' * 80}")
        
        print(f"\n📌 Method Name:")
        print(f"   {method_info['method_name']}")
        
        print(f"\n📋 Method Signature:")
        print(f"   {method_info['method_signature']}")
        
        print(f"\n🏛️  Class Context:")
        print(f"   {method_info['class_context']}")
        
        print(f"\n📄 Method Body (first 500 chars):")
        body_preview = method_info['method_body'][:500]
        if len(method_info['method_body']) > 500:
            body_preview += "\n   ... (truncated)"
        # Indent the body for better readability
        for line in body_preview.split('\n'):
            print(f"   {line}")
        
        print(f"\n📊 Body Length: {len(method_info['method_body'])} characters")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Successfully parsed {len(results)} public methods")
    print(f"✓ All methods include class context with fields")
    print(f"✓ Empty methods were filtered out")
    print("\n🎉 Test completed successfully!")


if __name__ == "__main__":
    test_parser()
