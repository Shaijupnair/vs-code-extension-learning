"""
Simple demo script to show parsed Java methods.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser.java_parser import JavaCodeParser


def main():
    # Test file path - using a file with proper package declaration
    test_file = r"E:\OpenSource\eclipse\swtbot\org.eclipse.swtbot\org.eclipse.swtbot.eclipse.finder\src\org\eclipse\swtbot\eclipse\finder\SWTWorkbenchBot.java"
    
    print("Parsing Java file...")
    print(f"File: {test_file}\n")
    
    # Initialize and parse
    parser = JavaCodeParser()
    results = parser.parse_file(test_file)
    
    print(f"Found {len(results)} public methods\n")
    print("=" * 60)
    
    # Show each method
    for i, method in enumerate(results, 1):
        print(f"\nMETHOD {i}:")
        print(f"  Name: {method['method_name']}")
        print(f"  Signature: {method['method_signature'][:80]}...")
        print(f"  Class Context: {method['class_context'][:80]}...")
        print(f"  Body Length: {len(method['method_body'])} chars")
    
    # Save to JSON for inspection
    output_file = Path(__file__).parent / "parsed_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nFull output saved to: {output_file}")
    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
