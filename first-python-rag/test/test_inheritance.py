"""
Test script for verifying inheritance context support.
Tests the hierarchy scanner and parser integration.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parser.hierarchy_scanner import build_project_map
from parser.java_parser import JavaCodeParser


def test_inheritance_context():
    """Test the complete inheritance context workflow."""
    test_dir = Path(__file__).parent / "inheritance_test"
    
    print("=" * 80)
    print("Testing Inheritance Context Support")
    print("=" * 80)
    
    # Step 1: Build hierarchy map
    print("\n📊 STEP 1: Building Project Hierarchy Map")
    print("─" * 80)
    
    hierarchy_file = test_dir / "project_hierarchy.json"
    hierarchy_map = build_project_map(str(test_dir), str(hierarchy_file))
    
    print(f"\n✓ Hierarchy map created with {len(hierarchy_map)} classes")
    
    # Display hierarchy
    print("\n📋 Hierarchy Map Contents:")
    for class_name, info in hierarchy_map.items():
        print(f"\n  {class_name}:")
        print(f"    Parent: {info.get('parent', 'None')}")
        print(f"    Methods: {info.get('methods', [])}")
    
    # Step 2: Parse with inheritance context
    print("\n\n📝 STEP 2: Parsing with Inheritance Context")
    print("─" * 80)
    
    # Parse Dog.java with inheritance context
    parser_with_hierarchy = JavaCodeParser(hierarchy_map_path=str(hierarchy_file))
    
    dog_file = test_dir / "Dog.java"
    print(f"\nParsing: {dog_file}")
    dog_results = parser_with_hierarchy.parse_file(str(dog_file))
    
    print(f"\n✓ Found {len(dog_results)} public methods in Dog class")
    
    # Show Dog's context (should include inherited methods from Animal)
    if dog_results:
        print("\n🐕 Dog Class Context:")
        print("─" * 80)
        dog_context = dog_results[0]['class_context']
        print(f"{dog_context}")
        
        print("\n📋 Dog Methods:")
        for i, method in enumerate(dog_results, 1):
            print(f"{i}. {method['method_name']}: {method['method_signature'][:60]}...")
    
    # Parse Cat.java
    cat_file = test_dir / "Cat.java"
    print(f"\n\nParsing: {cat_file}")
    cat_results = parser_with_hierarchy.parse_file(str(cat_file))
    
    print(f"\n✓ Found {len(cat_results)} public methods in Cat class")
    
    if cat_results:
        print("\n🐱 Cat Class Context:")
        print("─" * 80)
        cat_context = cat_results[0]['class_context']
        print(f"{cat_context}")
        
        print("\n📋 Cat Methods:")
        for i, method in enumerate(cat_results, 1):
            print(f"{i}. {method['method_name']}: {method['method_signature'][:60]}...")
    
    # Step 3: Compare with parser without hierarchy
    print("\n\n🔄 STEP 3: Comparison (Without Inheritance Context)")
    print("─" * 80)
    
    parser_without_hierarchy = JavaCodeParser()  # No hierarchy map
    dog_results_basic = parser_without_hierarchy.parse_file(str(dog_file))
    
    if dog_results_basic:
        print("\nDog Class Context (without inheritance):")
        print(dog_results_basic[0]['class_context'])
    
    # Step 4: Verification
    print("\n\n✅ VERIFICATION")
    print("=" * 80)
    
    # Check if Dog has inheritance info
    has_inheritance = 'Inherited Methods' in dog_results[0]['class_context']
    has_extends = 'Extends: Animal' in dog_results[0]['class_context']
    
    print(f"\n✓ Dog class has 'Extends' clause: {has_extends}")
    print(f"✓ Dog class has 'Inherited Methods': {has_inheritance}")
    
    if has_inheritance:
        # Extract inherited methods
        context = dog_results[0]['class_context']
        if 'Inherited Methods: [' in context:
            start = context.index('Inherited Methods: [') + len('Inherited Methods: [')
            end = context.index(']', start)
            inherited = context[start:end]
            inherited_list = [m.strip() for m in inherited.split(',')]
            
            print(f"\n📝 Inherited Methods from Animal:")
            for method in inherited_list:
                print(f"   - {method}")
            
            # Verify expected methods
            expected = ['eat', 'sleep', 'getName', 'makeSound']
            found_all = all(method in inherited_list for method in expected)
            print(f"\n✓ All expected methods found: {found_all}")
    
    # Save detailed results
    output_file = test_dir / "inheritance_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'dog_methods': dog_results,
            'cat_methods': cat_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("🎉 Inheritance Context Testing Completed Successfully!")
    print("=" * 80)


if __name__ == "__main__":
    test_inheritance_context()
