"""
Code Parser - Comprehensive code parsing for multiple languages.

Supports Python, JavaScript, Java, C++, and C with language-specific extraction.
"""

import ast
import re
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class CodeParser:
    """Parse code files and extract structure information."""

    SUPPORTED_LANGUAGES = ["python", "javascript", "java", "cpp", "c"]

    def __init__(self):
        """Initialize the code parser."""
        self.logger = logging.getLogger(f"{__name__}.CodeParser")

    def parse_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a code file and extract structure.

        Args:
            file_path: Path to the code file
            language: Programming language (auto-detect from extension if not provided)

        Returns:
            Dictionary containing parsed code structure
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Auto-detect language from file extension
            if not language:
                language = self._detect_language(file_path)

            return self.parse_content(content, language)
        except Exception as e:
            self.logger.error(f"Error parsing file {file_path}: {e}")
            return {"error": str(e), "file": file_path}

    def parse_content(self, content: str, language: str = "python") -> Dict[str, Any]:
        """
        Parse code content and extract structure.

        Args:
            content: Code content as string
            language: Programming language

        Returns:
            Dictionary containing parsed code structure
        """
        language = language.lower()

        if language == "python":
            return self._parse_python(content)
        elif language in ["javascript", "js"]:
            return self._parse_javascript(content)
        elif language == "java":
            return self._parse_java(content)
        elif language in ["cpp", "c++"]:
            return self._parse_cpp(content)
        elif language == "c":
            return self._parse_c(content)
        else:
            return {"error": f"Unsupported language: {language}"}

    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "javascript",
            ".tsx": "javascript",
            ".java": "java",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".h": "c",
        }

        for ext, lang in extension_map.items():
            if file_path.endswith(ext):
                return lang

        return "python"  # Default

    def _parse_python(self, content: str) -> Dict[str, Any]:
        """Parse Python code using AST."""
        try:
            tree = ast.parse(content)

            functions = []
            classes = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_python_function(node)
                    functions.append(func_info)

                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_python_class(node)
                    classes.append(class_info)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            lines = content.split("\n")
            return {
                "language": "python",
                "functions": functions,
                "classes": classes,
                "imports": list(set(imports)),
                "metrics": {
                    "total_lines": len(lines),
                    "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
                    "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
                    "function_count": len(functions),
                    "class_count": len(classes),
                    "import_count": len(set(imports)),
                },
            }

        except SyntaxError as e:
            return {"error": f"Syntax error: {e}", "language": "python"}

    def _extract_python_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract Python function information."""
        args = [arg.arg for arg in node.args.args]
        defaults = [repr(d) for d in node.args.defaults]

        return {
            "name": node.name,
            "line": node.lineno,
            "args": args,
            "defaults": defaults,
            "decorators": [ast.unparse(d) if hasattr(ast, "unparse") else str(d) for d in node.decorator_list],
        }

    def _extract_python_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract Python class information."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)

        bases = [ast.unparse(b) if hasattr(ast, "unparse") else str(b) for b in node.bases]

        return {
            "name": node.name,
            "line": node.lineno,
            "methods": methods,
            "bases": bases,
            "method_count": len(methods),
        }

    def _parse_javascript(self, content: str) -> Dict[str, Any]:
        """Parse JavaScript code using regex patterns."""
        functions = []
        classes = []
        imports = []

        # Function patterns
        function_pattern = r"(?:async\s+)?function\s+(\w+)\s*\((.*?)\)"
        for match in re.finditer(function_pattern, content):
            functions.append({
                "name": match.group(1),
                "args": [arg.strip() for arg in match.group(2).split(",") if arg.strip()],
            })

        # Arrow function patterns
        arrow_pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>"
        for match in re.finditer(arrow_pattern, content):
            functions.append({
                "name": match.group(1),
                "args": [arg.strip() for arg in match.group(2).split(",") if arg.strip()],
            })

        # Class patterns
        class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?"
        for match in re.finditer(class_pattern, content):
            classes.append({
                "name": match.group(1),
                "extends": match.group(2),
            })

        # Import patterns
        import_pattern = r"(?:import|require)\s+(?:\{.*?\}|.*?)\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))

        lines = content.split("\n")
        return {
            "language": "javascript",
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
            "metrics": {
                "total_lines": len(lines),
                "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("//")]),
                "comment_lines": len([l for l in lines if l.strip().startswith("//")]),
                "function_count": len(functions),
                "class_count": len(classes),
                "import_count": len(set(imports)),
            },
        }

    def _parse_java(self, content: str) -> Dict[str, Any]:
        """Parse Java code using regex patterns."""
        functions = []
        classes = []
        imports = []

        # Import patterns
        import_pattern = r"import\s+([\w.]+);"
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))

        # Class patterns
        class_pattern = r"(?:public\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?"
        for match in re.finditer(class_pattern, content):
            classes.append({
                "name": match.group(1),
                "extends": match.group(2),
            })

        # Method patterns
        method_pattern = r"(?:public|private|protected)\s+(?:static\s+)?(?:void|\w+)\s+(\w+)\s*\((.*?)\)"
        for match in re.finditer(method_pattern, content):
            args = [arg.split()[-1] for arg in match.group(2).split(",") if arg.strip()]
            functions.append({
                "name": match.group(1),
                "args": args,
            })

        lines = content.split("\n")
        return {
            "language": "java",
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
            "metrics": {
                "total_lines": len(lines),
                "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("//")]),
                "comment_lines": len([l for l in lines if l.strip().startswith("//")]),
                "function_count": len(functions),
                "class_count": len(classes),
                "import_count": len(set(imports)),
            },
        }

    def _parse_cpp(self, content: str) -> Dict[str, Any]:
        """Parse C++ code using regex patterns."""
        return self._parse_c_like(content, "cpp")

    def _parse_c(self, content: str) -> Dict[str, Any]:
        """Parse C code using regex patterns."""
        return self._parse_c_like(content, "c")

    def _parse_c_like(self, content: str, language: str) -> Dict[str, Any]:
        """Parse C/C++ code using regex patterns."""
        functions = []
        classes = []
        includes = []

        # Include patterns
        include_pattern = r"#include\s+[<\"]([^>\"]+)[>\"]"
        for match in re.finditer(include_pattern, content):
            includes.append(match.group(1))

        # Class/struct patterns (C++ only)
        if language == "cpp":
            class_pattern = r"(?:class|struct)\s+(\w+)(?:\s*:\s*(?:public|private)\s+(\w+))?"
            for match in re.finditer(class_pattern, content):
                classes.append({
                    "name": match.group(1),
                    "parent": match.group(2),
                })

        # Function patterns
        function_pattern = r"(?:\w+(?:\s+\*)?)\s+(\w+)\s*\((.*?)\)\s*(?:const)?\s*[{;]"
        for match in re.finditer(function_pattern, content):
            args = [arg.split()[-1] for arg in match.group(2).split(",") if arg.strip()]
            functions.append({
                "name": match.group(1),
                "args": args,
            })

        lines = content.split("\n")
        return {
            "language": language,
            "functions": functions,
            "classes": classes,
            "includes": list(set(includes)),
            "metrics": {
                "total_lines": len(lines),
                "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("//")]),
                "comment_lines": len([l for l in lines if l.strip().startswith("//")]),
                "function_count": len(functions),
                "class_count": len(classes),
                "include_count": len(set(includes)),
            },
        }

    def generate_structure_summary(self, parsed_code: Dict[str, Any]) -> str:
        """Generate a human-readable summary of code structure."""
        if "error" in parsed_code:
            return f"Parse Error: {parsed_code['error']}"

        summary = []
        summary.append(f"Language: {parsed_code.get('language', 'unknown')}")
        summary.append(f"Lines: {parsed_code.get('metrics', {}).get('total_lines', 0)}")

        if parsed_code.get("classes"):
            summary.append(f"Classes: {len(parsed_code['classes'])}")
            for cls in parsed_code["classes"][:3]:
                summary.append(f"  - {cls.get('name')}")

        if parsed_code.get("functions"):
            summary.append(f"Functions: {len(parsed_code['functions'])}")
            for func in parsed_code["functions"][:3]:
                summary.append(f"  - {func.get('name')}")

        if parsed_code.get("imports"):
            summary.append(f"Imports: {len(parsed_code['imports'])}")

        return "\n".join(summary)
