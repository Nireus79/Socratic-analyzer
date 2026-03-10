"""AST parsing utilities for code analysis."""

import ast
from typing import Any, Dict, List, Optional, Tuple


class ASTAnalyzer:
    """Utilities for analyzing Python AST."""

    @staticmethod
    def parse_code(code: str) -> Optional[ast.Module]:
        """Parse Python code into AST.

        Args:
            code: Python source code

        Returns:
            AST Module object or None if parsing fails
        """
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    @staticmethod
    def get_functions(tree: ast.AST) -> List[ast.FunctionDef]:
        """Get all function definitions from AST.

        Args:
            tree: AST tree to analyze

        Returns:
            List of FunctionDef nodes
        """
        return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    @staticmethod
    def get_classes(tree: ast.AST) -> List[ast.ClassDef]:
        """Get all class definitions from AST.

        Args:
            tree: AST tree to analyze

        Returns:
            List of ClassDef nodes
        """
        return [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    @staticmethod
    def get_imports(tree: ast.AST) -> Tuple[List[str], List[str]]:
        """Get all imports from AST.

        Args:
            tree: AST tree to analyze

        Returns:
            Tuple of (import_names, from_imports)
        """
        imports = []
        from_imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    from_imports.append(f"from {module} import {alias.name}")

        return imports, from_imports

    @staticmethod
    def get_function_info(func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Get detailed information about a function.

        Args:
            func_node: FunctionDef AST node

        Returns:
            Dictionary with function information
        """
        # Get docstring
        docstring = ast.get_docstring(func_node) or ""

        # Get parameters
        args = func_node.args
        params = []
        if args.args:
            params.extend(arg.arg for arg in args.args)
        if args.kwonlyargs:
            params.extend(arg.arg for arg in args.kwonlyargs)
        if args.vararg:
            params.append(f"*{args.vararg.arg}")
        if args.kwarg:
            params.append(f"**{args.kwarg.arg}")

        # Count statements
        num_statements = len(func_node.body)

        # Check for type hints
        has_return_type = func_node.returns is not None
        has_param_types = any(arg.annotation is not None for arg in args.args)

        return {
            "name": func_node.name,
            "lineno": func_node.lineno,
            "col_offset": func_node.col_offset,
            "docstring": docstring,
            "has_docstring": bool(docstring),
            "parameters": params,
            "param_count": len(params),
            "statements": num_statements,
            "has_return_type": has_return_type,
            "has_param_types": has_param_types,
        }

    @staticmethod
    def get_class_info(class_node: ast.ClassDef) -> Dict[str, Any]:
        """Get detailed information about a class.

        Args:
            class_node: ClassDef AST node

        Returns:
            Dictionary with class information
        """
        # Get docstring
        docstring = ast.get_docstring(class_node) or ""

        # Get methods
        methods = [
            node.name
            for node in class_node.body
            if isinstance(node, ast.FunctionDef)
        ]

        # Get base classes
        bases = []
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)

        return {
            "name": class_node.name,
            "lineno": class_node.lineno,
            "col_offset": class_node.col_offset,
            "docstring": docstring,
            "has_docstring": bool(docstring),
            "methods": methods,
            "method_count": len(methods),
            "bases": bases,
            "base_count": len(bases),
        }

    @staticmethod
    def count_lines(code: str) -> int:
        """Count non-empty, non-comment lines.

        Args:
            code: Source code

        Returns:
            Line count
        """
        lines = code.split("\n")
        count = 0

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                count += 1

        return count

    @staticmethod
    def count_blank_lines(code: str) -> int:
        """Count blank lines.

        Args:
            code: Source code

        Returns:
            Blank line count
        """
        lines = code.split("\n")
        return sum(1 for line in lines if not line.strip())

    @staticmethod
    def get_max_line_length(code: str) -> int:
        """Get maximum line length.

        Args:
            code: Source code

        Returns:
            Maximum line length
        """
        lines = code.split("\n")
        return max(len(line) for line in lines) if lines else 0

    @staticmethod
    def find_long_lines(code: str, max_length: int = 120) -> List[Tuple[int, int]]:
        """Find lines exceeding max length.

        Args:
            code: Source code
            max_length: Maximum allowed line length

        Returns:
            List of (line_number, actual_length) tuples
        """
        lines = code.split("\n")
        long_lines = []

        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                long_lines.append((i, len(line)))

        return long_lines

    @staticmethod
    def find_unused_variables(tree: ast.AST, file_path: str = "") -> List[Tuple[str, int]]:
        """Find potentially unused variables.

        Args:
            tree: AST tree
            file_path: File path for reference

        Returns:
            List of (variable_name, line_number) tuples
        """
        # Simple implementation: find assignments not in function arguments
        unused = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get parameter names
                params = set()
                if node.args.args:
                    params.update(arg.arg for arg in node.args.args)

                # Find assignments in function
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                var_name = target.id
                                if var_name not in params and var_name.startswith("_"):
                                    continue
                                # Check if used later
                                # This is a simplified check
                                if not var_name.isupper():
                                    unused.append((var_name, getattr(child, "lineno", 0)))

        return unused
