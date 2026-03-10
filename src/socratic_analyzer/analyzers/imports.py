"""Import analysis."""

import ast
from typing import List

from socratic_analyzer.analyzers.base import BaseAnalyzer
from socratic_analyzer.models import CodeIssue
from socratic_analyzer.utils.ast_parser import ASTAnalyzer


class ImportAnalyzer(BaseAnalyzer):
    """Analyze imports in code."""

    @property
    def name(self) -> str:
        """Analyzer name."""
        return "ImportAnalyzer"

    @property
    def description(self) -> str:
        """Analyzer description."""
        return "Analyzes import organization and issues"

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze imports.

        Args:
            code: Source code to analyze
            file_path: Path to the file

        Returns:
            List of import issues
        """
        issues = []

        # Parse code
        tree = ASTAnalyzer.parse_code(code)
        if tree is None:
            return issues

        # Check import organization
        issues.extend(self._check_import_organization(tree, file_path))

        # Check for unused imports
        issues.extend(self._check_unused_imports(tree, code, file_path))

        # Check for circular imports
        issues.extend(self._check_import_issues(tree, file_path))

        return issues

    def _check_import_organization(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check if imports are properly organized.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        imports = []
        from_imports = []
        first_import_line = None

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.append(node.lineno)
                if first_import_line is None:
                    first_import_line = node.lineno
            elif isinstance(node, ast.ImportFrom):
                from_imports.append(node.lineno)
                if first_import_line is None:
                    first_import_line = node.lineno

        # Check if imports are grouped (simple heuristic)
        if imports and from_imports:
            # Standard convention: stdlib, then third-party, then local
            # Just check they're not scattered
            all_imports = sorted(imports + from_imports)
            gaps = [all_imports[i + 1] - all_imports[i] for i in range(len(all_imports) - 1)]

            if gaps and max(gaps) > 2:
                issues.append(
                    CodeIssue(
                        issue_type="style",
                        severity="low",
                        location=self._format_location(file_path, first_import_line or 1),
                        message="Imports are not grouped together",
                        suggestion="Group all imports at the top of the file",
                    )
                )

        return issues

    def _check_unused_imports(self, tree: ast.AST, code: str, file_path: str) -> List[CodeIssue]:
        """Check for unused imports.

        Args:
            tree: AST tree
            code: Source code
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        # Collect all imports
        imports_dict = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports_dict[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name != "*":
                        imports_dict[name] = node.lineno

        # Check which are used
        for name, lineno in imports_dict.items():
            # Look for uses of this import in the code
            # Simple check: look for the name in non-import lines
            lines = code.split("\n")

            used = False
            for i, line in enumerate(lines[lineno:], start=lineno + 1):
                # Skip import lines
                if "import" in line:
                    continue
                # Check if name is used (simple)
                if name in line and not line.strip().startswith("#"):
                    used = True
                    break

            if not used:
                issues.append(
                    CodeIssue(
                        issue_type="style",
                        severity="low",
                        location=self._format_location(file_path, lineno),
                        message=f"Unused import: {name}",
                        suggestion=f"Remove unused import '{name}'",
                    )
                )

        return issues

    def _check_import_issues(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check for various import issues.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Check for relative imports beyond current package
                if node.level is not None and node.level > 1:
                    issues.append(
                        CodeIssue(
                            issue_type="style",
                            severity="low",
                            location=self._format_location(file_path, node.lineno),
                            message="Uses multiple-level relative import",
                            suggestion="Avoid deep relative imports, use absolute imports instead",
                        )
                    )

        return issues
