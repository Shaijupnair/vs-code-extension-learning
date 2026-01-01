"""
Hierarchy Scanner for Java Projects.
Builds a project-wide map of class inheritance and public methods.
"""

import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from pathlib import Path
import json
from typing import Dict, List, Optional
from tqdm import tqdm


class HierarchyScanner:
    """
    Scans a Java project to build a hierarchy map of classes, parents, and methods.
    """
    
    def __init__(self):
        """Initialize the tree-sitter Java parser."""
        self.JAVA_LANGUAGE = Language(tsjava.language())
        self.parser = Parser(self.JAVA_LANGUAGE)
    
    def build_project_map(self, root_path: str, output_file: str = "project_hierarchy.json") -> Dict:
        """
        Walk through all .java files and build a hierarchy map.
        
        Args:
            root_path: Root directory to scan for Java files
            output_file: Output JSON file path (relative to root_path or absolute)
            
        Returns:
            Dictionary mapping class names to their metadata
        """
        root_path = Path(root_path)
        
        if not root_path.exists():
            raise FileNotFoundError(f"Root path not found: {root_path}")
        
        # Find all Java files
        java_files = list(root_path.rglob("*.java"))
        print(f"Found {len(java_files)} Java files")
        
        # Build hierarchy map
        hierarchy_map = {}
        
        print("Scanning files for class hierarchy...")
        for java_file in tqdm(java_files, desc="Processing"):
            try:
                class_info = self._extract_class_info(java_file)
                if class_info:
                    # Add each class found in the file
                    for class_name, info in class_info.items():
                        hierarchy_map[class_name] = info
            except Exception as e:
                print(f"\n⚠️  Error processing {java_file}: {e}")
                continue
        
        # Determine output path
        if Path(output_file).is_absolute():
            output_path = Path(output_file)
        else:
            output_path = root_path / output_file
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(hierarchy_map, f, indent=2)
        
        print(f"\n✓ Hierarchy map saved to: {output_path}")
        print(f"✓ Total classes mapped: {len(hierarchy_map)}")
        
        return hierarchy_map
    
    def _extract_class_info(self, file_path: Path) -> Dict[str, Dict]:
        """
        Extract class information from a single Java file.
        
        Returns:
            Dictionary mapping class names to their info (parent, methods)
        """
        # Read source code
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        # Parse
        tree = self.parser.parse(bytes(source_code, 'utf8'))
        root_node = tree.root_node
        
        # Extract package name for fully qualified names
        package_name = self._extract_package_name(root_node, source_code)
        
        # Find all classes in this file
        class_info = {}
        class_nodes = self._find_nodes_by_type(root_node, 'class_declaration')
        
        for class_node in class_nodes:
            class_name = self._get_class_name(class_node, source_code)
            if not class_name:
                continue
            
            # Get parent class (extends)
            parent_name = self._get_parent_class(class_node, source_code)
            
            # Get public method names
            public_methods = self._get_public_method_names(class_node, source_code)
            
            # Store with fully qualified name if package exists
            if package_name and package_name != "None":
                full_class_name = f"{package_name}.{class_name}"
            else:
                full_class_name = class_name
            
            class_info[full_class_name] = {
                "parent": parent_name,
                "methods": public_methods,
                "simple_name": class_name
            }
        
        return class_info
    
    def _find_nodes_by_type(self, node, node_type: str) -> List:
        """Recursively find all nodes of a specific type."""
        results = []
        
        if node.type == node_type:
            results.append(node)
        
        for child in node.children:
            results.extend(self._find_nodes_by_type(child, node_type))
        
        return results
    
    def _extract_package_name(self, root_node, source_code: str) -> str:
        """Extract the package name from the file."""
        for child in root_node.children:
            if child.type == 'package_declaration':
                for package_child in child.children:
                    if package_child.type in ['scoped_identifier', 'identifier']:
                        return source_code[package_child.start_byte:package_child.end_byte]
        return "None"
    
    def _get_class_name(self, class_node, source_code: str) -> Optional[str]:
        """Extract the class name from a class declaration node."""
        for child in class_node.children:
            if child.type == 'identifier':
                return child.text.decode('utf8')
        return None
    
    def _get_parent_class(self, class_node, source_code: str) -> Optional[str]:
        """
        Extract the parent class name from extends clause.
        Returns None if class doesn't extend anything.
        """
        for child in class_node.children:
            if child.type == 'superclass':
                # The superclass node contains the type being extended
                for superclass_child in child.children:
                    if superclass_child.type in ['type_identifier', 'generic_type', 'scoped_type_identifier']:
                        parent_name = source_code[superclass_child.start_byte:superclass_child.end_byte]
                        # Clean up generics if present
                        if '<' in parent_name:
                            parent_name = parent_name.split('<')[0]
                        return parent_name.strip()
        return None
    
    def _get_public_method_names(self, class_node, source_code: str) -> List[str]:
        """
        Extract names of all public methods in this class.
        """
        method_names = []
        
        # Find class body
        class_body = None
        for child in class_node.children:
            if child.type == 'class_body':
                class_body = child
                break
        
        if not class_body:
            return method_names
        
        # Find all method declarations
        for child in class_body.children:
            if child.type == 'method_declaration':
                # Check if public
                is_public = False
                method_name = None
                
                for method_child in child.children:
                    if method_child.type == 'modifiers':
                        modifiers_text = source_code[method_child.start_byte:method_child.end_byte]
                        if 'public' in modifiers_text:
                            is_public = True
                    elif method_child.type == 'identifier':
                        method_name = method_child.text.decode('utf8')
                
                if is_public and method_name:
                    method_names.append(method_name)
        
        return method_names


def build_project_map(root_path: str, output_file: str = "project_hierarchy.json") -> Dict:
    """
    Convenience function to build project hierarchy map.
    
    Args:
        root_path: Root directory to scan for Java files
        output_file: Output JSON file path
        
    Returns:
        Dictionary mapping class names to their metadata
    """
    scanner = HierarchyScanner()
    return scanner.build_project_map(root_path, output_file)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        print("Usage: python hierarchy_scanner.py <project_root_path>")
        sys.exit(1)
    
    build_project_map(root)
