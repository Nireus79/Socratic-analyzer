"""Static code analysis for detecting issues and violations."""

import ast
from typing import List

from socratic_analyzer.analyzers.base import BaseAnalyzer
from socratic_analyzer.models import CodeIssue
from socratic_analyzer.utils.ast_parser import ASTAnalyzer


class StaticAnalyzer(BaseAnalyzer):
    """Detect code issues and violations."""

    @property
    def name(self) -> str:
        """Analyzer name."""
        return "StaticAnalyzer"

    @property
    def description(self) -> str:
        """Analyzer description."""
        return "Detects code issues, violations, and code smells"

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze code for issues.

        Args:
            code: Source code to analyze
            file_path: Path to the file

        Returns:
            List of detected issues
        """
        issues = []

        # Parse code
        tree = ASTAnalyzer.parse_code(code)
        if tree is None:
            issues.append(
                CodeIssue(
                    issue_type="syntax",
                    severity="critical",
                    location=self._format_location(file_path, 1),
                    message="Syntax error in code",
                    suggestion="Fix syntax errors before analysis",
                )
            )
            return issues

        # Check for unused variables
        issues.extend(self._check_unused_variables(tree, file_path))

        # Check for missing docstrings
        issues.extend(self._check_missing_docstrings(tree, file_path))

        # Check for long lines
        issues.extend(self._check_long_lines(code, file_path))

        # Check for empty blocks
        issues.extend(self._check_empty_blocks(tree, file_path))

        # Check imports
        issues.extend(self._check_imports(tree, file_path))

        return issues

    def _check_unused_variables(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check for unused variables.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get parameter names
                params = set()
                if node.args.args:
                    params.update(arg.arg for arg in node.args.args)

                # Find assignments that might be unused
                assignments = {}
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                var_name = target.id
                                if not var_name.startswith("_"):
                                    assignments[var_name] = getattr(child, "lineno", 0)

                # Check usage (simplified)
                used_vars = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name) and isinstance(
                        child.ctx, ast.Load
                    ):
                        used_vars.add(child.id)

                # Find unused
                for var_name, lineno in assignments.items():
                    if var_name not in used_vars and var_name not in params:
                        issues.append(
                            CodeIssue(
                                issue_type="style",
                                severity="low",
                                location=self._format_location(file_path, lineno),
                                message=f"Variable '{var_name}' assigned but not used",
                                suggestion=f"Remove unused variable '{var_name}' or use it",
                            )
                        )

        return issues

    def _check_missing_docstrings(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check for missing docstrings.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        # Check module docstring
        if not ast.get_docstring(tree):
            issues.append(
                CodeIssue(
                    issue_type="maintenance",
                    severity="low",
                    location=self._format_location(file_path, 1),
                    message="Module missing docstring",
                    suggestion='Add module docstring at the top: """Description."""',
                )
            )

        # Check function docstrings
        for func in ASTAnalyzer.get_functions(tree):
            if not ast.get_docstring(func):
                issues.append(
                    CodeIssue(
                        issue_type="maintenance",
                        severity="low",
                        location=self._format_location(file_path, func.lineno),
                        message=f"Function '{func.name}' missing docstring",
                        suggestion=f'Add docstring: def {func.name}():\n    """Description."""',
                    )
                )

        # Check class docstrings
        for cls in ASTAnalyzer.get_classes(tree):
            if not ast.get_docstring(cls):
                issues.append(
                    CodeIssue(
                        issue_type="maintenance",
                        severity="low",
                        location=self._format_location(file_path, cls.lineno),
                        message=f"Class '{cls.name}' missing docstring",
                        suggestion=f'Add docstring: class {cls.name}:\n    """Description."""',
                    )
                )

        return issues

    def _check_long_lines(self, code: str, file_path: str, max_length: int = 120) -> List[CodeIssue]:
        """Check for lines exceeding max length.

        Args:
            code: Source code
            file_path: File path
            max_length: Maximum allowed line length

        Returns:
            List of issues
        """
        issues = []
        lines = code.split("\n")

        for lineno, line in enumerate(lines, 1):
            if len(line) > max_length:
                issues.append(
                    CodeIssue(
                        issue_type="style",
                        severity="low",
                        location=self._format_location(file_path, lineno),
                        message=f"Line too long ({len(line)} > {max_length} characters)",
                        suggestion="Break long lines into multiple lines",
                    )
                )

        return issues

    def _check_empty_blocks(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check for empty function/class bodies.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Check if body only contains pass or docstring
                body = node.body
                if not body:
                    continue

                # Filter out docstrings
                body_without_docs = [
                    n for n in body if not isinstance(n, ast.Expr) or
                    not isinstance(n.value, ast.Constant)
                ]

                # Check for only pass statements
                if len(body_without_docs) == 0 or all(
                    isinstance(n, ast.Pass) for n in body_without_docs
                ):
                    node_type = "Function" if isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ) else "Class"

                    issues.append(
                        CodeIssue(
                            issue_type="style",
                            severity="medium",
                            location=self._format_location(file_path, node.lineno),
                            message=f"{node_type} '{node.name}' has empty body",
                            suggestion=f"Implement {node_type.lower()} or remove it",
                        )
                    )

        return issues

    def _check_imports(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check import organization.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []
        imports, from_imports = ASTAnalyzer.get_imports(tree)

        # Check for wildcard imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        issues.append(
                            CodeIssue(
                                issue_type="style",
                                severity="medium",
                                location=self._format_location(file_path, node.lineno),
                                message="Wildcard import detected",
                                suggestion="Use explicit imports instead of 'from x import *'",
                            )
                        )

        return issues
