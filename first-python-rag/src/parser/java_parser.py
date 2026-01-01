"""
Java Code Parser using Tree-Sitter for structural code analysis.
Extracts classes, fields, and public methods from Java source files.
"""

import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from pathlib import Path
from typing import List, Dict, Optional


class JavaCodeParser:
    """
    Structural parser for Java code using tree-sitter.
    Extracts classes, fields, and public methods with full context.
    Supports inheritance context from project hierarchy.
    """
    
    def __init__(self, hierarchy_map_path: Optional[str] = None):
        """
        Initialize the tree-sitter Java parser.
        
        Args:
            hierarchy_map_path: Optional path to project_hierarchy.json file
                               for inheritance context support
        """
        self.JAVA_LANGUAGE = Language(tsjava.language())
        self.parser = Parser(self.JAVA_LANGUAGE)
        
        # Load hierarchy map if provided
        self.hierarchy_map = {}
        if hierarchy_map_path:
            self._load_hierarchy_map(hierarchy_map_path)
    
    def parse_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        Parse a Java file and extract public methods with their context.
        
        Args:
            file_path: Path to the .java file
            
        Returns:
            List of dictionaries containing method information:
            - id: Unique identifier for the method (handles overloading)
            - method_name: Name of the method
            - method_signature: Full normalized method signature
            - method_body: Complete method code
            - class_context: Package name, class name and field definitions
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read the source code
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source_code = f.read()
        
        # Parse the code
        tree = self.parser.parse(bytes(source_code, 'utf8'))
        root_node = tree.root_node
        
        # Extract package name
        package_name = self._extract_package_name(root_node, source_code)
        
        # Extract all methods with context
        results = []
        
        # Find all class declarations
        for class_node in self._find_nodes_by_type(root_node, 'class_declaration'):
            class_name = self._get_class_name(class_node)
            fields = self._extract_fields(class_node, source_code)
            
            # Extract parent class for inheritance context
            parent_class = self._get_parent_class(class_node, source_code)
            
            # Build class context with inheritance
            class_context = self._format_class_context(
                package_name, 
                class_name, 
                fields, 
                parent_class
            )
            
            # Extract public methods from this class
            for method_node in self._find_nodes_by_type(class_node, 'method_declaration'):
                if self._is_public_method(method_node, source_code):
                    method_info = self._extract_method_info(
                        method_node, 
                        source_code, 
                        class_context,
                        class_name,
                        is_constructor=False
                    )
                    
                    # Filter out empty methods
                    if method_info and not self._is_empty_method(method_info['method_body']):
                        # Generate unique ID for this method
                        method_info['id'] = self._generate_method_id(
                            class_context, 
                            method_info['method_signature']
                        )
                        results.append(method_info)
            
            # Extract public constructors from this class
            for constructor_node in self._find_nodes_by_type(class_node, 'constructor_declaration'):
                if self._is_public_method(constructor_node, source_code):
                    constructor_info = self._extract_method_info(
                        constructor_node,
                        source_code,
                        class_context,
                        class_name,
                        is_constructor=True
                    )
                    
                    # Filter out empty constructors
                    if constructor_info and not self._is_empty_method(constructor_info['method_body']):
                        # Generate unique ID for this constructor
                        constructor_info['id'] = self._generate_method_id(
                            class_context,
                            constructor_info['method_signature']
                        )
                        results.append(constructor_info)
        
        return results
    
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
                # Find the scoped_identifier or identifier within package declaration
                for package_child in child.children:
                    if package_child.type in ['scoped_identifier', 'identifier']:
                        return source_code[package_child.start_byte:package_child.end_byte]
                # Fallback: extract text between 'package' and ';'
                package_text = source_code[child.start_byte:child.end_byte]
                package_text = package_text.replace('package', '').replace(';', '').strip()
                return package_text
        return "None"
    
    def _get_class_name(self, class_node) -> str:
        """Extract the class name from a class declaration node."""
        for child in class_node.children:
            if child.type == 'identifier':
                return child.text.decode('utf8')
        return "UnknownClass"
    
    def _extract_fields(self, class_node, source_code: str) -> List[str]:
        """Extract all field declarations from a class."""
        fields = []
        
        # Find the class body
        class_body = None
        for child in class_node.children:
            if child.type == 'class_body':
                class_body = child
                break
        
        if not class_body:
            return fields
        
        # Extract field declarations
        for child in class_body.children:
            if child.type == 'field_declaration':
                field_text = source_code[child.start_byte:child.end_byte].strip()
                # Clean up the field text (remove newlines, extra spaces)
                field_text = ' '.join(field_text.split())
                fields.append(field_text)
        
        return fields
    
    def _format_class_context(
        self, 
        package_name: str, 
        class_name: str, 
        fields: List[str],
        parent_class: Optional[str] = None
    ) -> str:
        """
        Format the class context string with package, class, fields, and inheritance.
        """
        package_str = f"Package: {package_name}" if package_name else "Package: None"
        
        # Base context
        if fields:
            fields_str = "; ".join(fields)
            context = f"{package_str}, Class: {class_name}, Fields: {fields_str}"
        else:
            context = f"{package_str}, Class: {class_name}, Fields: None"
        
        # Add inheritance information if available
        if parent_class:
            context += f", Extends: {parent_class}"
            
            # Look up inherited methods from hierarchy map
            inherited_methods = self._get_inherited_methods(parent_class)
            if inherited_methods:
                methods_str = ", ".join(inherited_methods)
                context += f", Inherited Methods: [{methods_str}]"
        
        return context
    
    def _is_public_method(self, method_node, source_code: str) -> bool:
        """Check if a method has the public modifier."""
        # Look for modifiers node
        for child in method_node.children:
            if child.type == 'modifiers':
                modifiers_text = source_code[child.start_byte:child.end_byte]
                return 'public' in modifiers_text
        return False
    
    def _extract_method_info(
        self, 
        method_node, 
        source_code: str, 
        class_context: str,
        class_name: str,
        is_constructor: bool = False
    ) -> Optional[Dict[str, str]]:
        """
        Extract method/constructor name, normalized signature, body, and dependencies.
        
        The signature follows the format:
        [Modifiers] [ReturnType] [MethodName]([ParameterType1] [ParamName1], ...)
        
        For constructors:
        [Modifiers] <Constructor> [ClassName]([Parameters])
        """
        method_name = None
        method_body = None
        modifiers = []
        return_type = None
        parameters = []
        parameter_types = []
        
        # Extract components from method node
        for child in method_node.children:
            if child.type == 'modifiers':
                # Extract all modifiers (public, static, final, etc.)
                modifiers_text = source_code[child.start_byte:child.end_byte]
                modifiers = modifiers_text.split()
                
            elif child.type == 'identifier':
                # Method name (for constructors, this is the class name)
                method_name = child.text.decode('utf8')
                
            elif child.type in ['type_identifier', 'void_type', 'integral_type', 'floating_point_type', 
                                'boolean_type', 'generic_type', 'array_type', 'scoped_type_identifier']:
                # Return type (not present for constructors)
                return_type = source_code[child.start_byte:child.end_byte].strip()
                
            elif child.type == 'formal_parameters':
                # Extract parameters and their types
                parameters, parameter_types = self._extract_parameters_with_types(child, source_code)
                
            elif child.type in ['block', 'constructor_body']:
                # Method body
                method_body = source_code[child.start_byte:child.end_byte].strip()
        
        # Handle constructor naming
        if is_constructor:
            method_name = f"<Constructor>"
            return_type = None  # Constructors don't have return types
        elif not method_name:
            return None
        
        # If we didn't find a body, extract the entire method
        if not method_body:
            method_body = source_code[method_node.start_byte:method_node.end_byte].strip()
        
        # Extract dependency types (filter out primitives and common types)
        dependency_types = self._filter_complex_types(parameter_types)
        
        # Build normalized signature
        modifiers_str = ' '.join(modifiers) if modifiers else ''
        params_str = ', '.join(parameters) if parameters else ''
        
        # Construct the complete signature
        signature_parts = []
        if modifiers_str:
            signature_parts.append(modifiers_str)
        
        if is_constructor:
            signature_parts.append('<Constructor>')
            signature_parts.append(f"{class_name}({params_str})")
        else:
            return_type_str = return_type if return_type else 'void'
            signature_parts.append(return_type_str)
            signature_parts.append(f"{method_name}({params_str})")
        
        method_signature = ' '.join(signature_parts)
        
        return {
            'method_name': method_name,
            'method_signature': method_signature,
            'method_body': method_body,
            'class_context': class_context,
            'dependency_types': dependency_types
        }
    
    def _is_empty_method(self, method_body: str) -> bool:
        """Check if a method body is empty or only contains whitespace/comments."""
        # Remove the surrounding braces and whitespace
        body = method_body.strip()
        if body.startswith('{') and body.endswith('}'):
            body = body[1:-1].strip()
        
        # Check if empty or only has comments
        if not body:
            return True
        
        # Simple check for single-line or multi-line comments only
        lines = [line.strip() for line in body.split('\n')]
        non_comment_lines = [
            line for line in lines 
            if line and not line.startswith('//') and not line.startswith('/*') and not line.startswith('*')
        ]
        
        return len(non_comment_lines) == 0
    
    def _extract_parameters(self, formal_params_node, source_code: str) -> List[str]:
        """
        Extract parameters from a formal_parameters node.
        
        Returns a list of strings in format: "Type paramName"
        Example: ["int base", "String name"]
        
        This is a convenience wrapper around _extract_parameters_with_types.
        """
        parameters, _ = self._extract_parameters_with_types(formal_params_node, source_code)
        return parameters
    
    def _extract_parameters_with_types(self, formal_params_node, source_code: str) -> tuple[List[str], List[str]]:
        """
        Extract parameters from a formal_parameters node with type information.
        
        Returns:
            tuple: (formatted_parameters, parameter_types)
            - formatted_parameters: ["Type paramName", ...]
            - parameter_types: ["Type", ...] (raw types for dependency analysis)
        """
        parameters = []
        parameter_types = []
        
        for child in formal_params_node.children:
            if child.type == 'formal_parameter':
                param_type = None
                param_name = None
                
                for param_child in child.children:
                    # Extract parameter type
                    if param_child.type in ['type_identifier', 'integral_type', 'floating_point_type',
                                           'boolean_type', 'generic_type', 'array_type', 
                                           'scoped_type_identifier', 'void_type']:
                        param_type = source_code[param_child.start_byte:param_child.end_byte].strip()
                    
                    # Extract parameter name
                    elif param_child.type == 'identifier':
                        param_name = param_child.text.decode('utf8')
                
                # Store the type for dependency tracking
                if param_type:
                    # Clean up generics for type extraction
                    clean_type = param_type.split('<')[0].strip()
                    # Remove array brackets
                    clean_type = clean_type.replace('[]', '').strip()
                    parameter_types.append(clean_type)
                
                # Combine type and name for signature
                if param_type and param_name:
                    parameters.append(f"{param_type} {param_name}")
                elif param_type:
                    # Sometimes name might be missing, use just type
                    parameters.append(param_type)
        
        return parameters, parameter_types
    
    def _generate_method_id(self, class_context: str, method_signature: str) -> str:
        """
        Generate a unique ID for a method based on its class context and signature.
        
        This ensures overloaded methods get different IDs.
        Uses SHA256 hash for consistent, unique identification.
        """
        import hashlib
        
        # Combine class context and signature for uniqueness
        unique_string = f"{class_context}::{method_signature}"
        
        # Generate hash
        hash_object = hashlib.sha256(unique_string.encode('utf-8'))
        method_id = hash_object.hexdigest()
        
        return method_id
    
    def _load_hierarchy_map(self, hierarchy_map_path: str):
        """Load the project hierarchy map from JSON file."""
        import json
        try:
            with open(hierarchy_map_path, 'r', encoding='utf-8') as f:
                self.hierarchy_map = json.load(f)
            print(f"✓ Loaded hierarchy map with {len(self.hierarchy_map)} classes")
        except FileNotFoundError:
            print(f"⚠️  Hierarchy map not found: {hierarchy_map_path}")
            self.hierarchy_map = {}
        except Exception as e:
            print(f"⚠️  Error loading hierarchy map: {e}")
            self.hierarchy_map = {}
    
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
    
    def _get_inherited_methods(self, parent_class: str) -> List[str]:
        """
        Recursively get all inherited public methods from parent class.
        
        Args:
            parent_class: Name of the parent class
            
        Returns:
            List of inherited method names
        """
        if not self.hierarchy_map:
            return []
        
        inherited_methods = []
        
        # Try exact match first
        if parent_class in self.hierarchy_map:
            parent_info = self.hierarchy_map[parent_class]
        else:
            # Try to find by simple name (in case of different package)
            parent_info = None
            for class_name, info in self.hierarchy_map.items():
                if info.get('simple_name') == parent_class or class_name.endswith(f".{parent_class}"):
                    parent_info = info
                    break
        
        if not parent_info:
            # Parent not in our codebase (e.g., standard library)
            return []
        
        # Add parent's methods
        if 'methods' in parent_info:
            inherited_methods.extend(parent_info['methods'])
        
        # Recursively get grandparent's methods
        if parent_info.get('parent'):
            grandparent_methods = self._get_inherited_methods(parent_info['parent'])
            inherited_methods.extend(grandparent_methods)
        
        return inherited_methods
    
    def _filter_complex_types(self, parameter_types: List[str]) -> List[str]:
        """
        Filter out primitive types and common Java types, keeping only custom types.
        
        Args:
            parameter_types: List of parameter type names
            
        Returns:
            List of complex/custom types that are dependencies
        """
        # Primitive types and common Java types to ignore
        primitives_and_common = {
            # Primitives
            'int', 'Integer', 'long', 'Long', 'short', 'Short',
            'byte', 'Byte', 'float', 'Float', 'double', 'Double',
            'boolean', 'Boolean', 'char', 'Character',
            'void', 'Void',
            # Common Java types
            'String', 'Object',
            # Common collections (often interfaces, don't need constructors)
            'List', 'ArrayList', 'Set', 'HashSet', 'Map', 'HashMap',
            'Collection', 'Iterable', 'Iterator',
            # Other common types
            'Optional', 'Stream'
        }
        
        complex_types = []
        for param_type in parameter_types:
            # Skip if primitive or common type
            if param_type not in primitives_and_common:
                # Keep custom types
                complex_types.append(param_type)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_complex_types = []
        for t in complex_types:
            if t not in seen:
                seen.add(t)
                unique_complex_types.append(t)
        
        return unique_complex_types

