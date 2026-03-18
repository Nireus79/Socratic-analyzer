"""Code Structure Analyzer - Analyze code structure and organization."""

import ast
import logging

logger = logging.getLogger(__name__)


class CodeStructureAnalyzer:
    """Analyze code structure using AST"""

    def __init__(self):
        logger.debug("CodeStructureAnalyzer initialized")

    def analyze(self, code: str, language: str = "python") -> dict:
        """Analyze code structure"""
        if language == "python":
            return self._analyze_python(code)
        return {"classes": [], "functions": [], "imports": []}

    def _analyze_python(self, code: str) -> dict:
        """Analyze Python code structure"""
        try:
            tree = ast.parse(code)
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = [
                node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)
            ]

            return {
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "language": "python",
                "lines_of_code": len(code.split("\n")),
            }
        except SyntaxError as e:
            logger.error(f"Failed to analyze Python code: {e}")
            return {"error": str(e), "language": "python"}

    def suggest_file_organization(self, code: str, language: str = "python") -> dict:
        """Suggest file organization"""
        analysis = self.analyze(code, language)
        if "error" in analysis:
            return {}

        suggestions = []
        if len(analysis.get("classes", [])) > 5:
            suggestions.append("Consider splitting into multiple files by class")
        if len(analysis.get("functions", [])) > 10:
            suggestions.append("Consider grouping related functions into classes")

        return {"suggestions": suggestions}
