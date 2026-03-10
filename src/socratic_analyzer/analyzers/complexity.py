"""Complexity analysis including cyclomatic complexity."""

import ast
from typing import List, Optional

from socratic_analyzer.analyzers.base import BaseAnalyzer
from socratic_analyzer.models import CodeIssue
from socratic_analyzer.utils.ast_parser import ASTAnalyzer


class ComplexityAnalyzer(BaseAnalyzer):
    """Analyze code complexity metrics."""

    def __init__(self, max_complexity: int = 10) -> None:
        """Initialize complexity analyzer.

        Args:
            max_complexity: Maximum allowed cyclomatic complexity
        """
        self.max_complexity = max_complexity

    @property
    def name(self) -> str:
        """Analyzer name."""
        return "ComplexityAnalyzer"

    @property
    def description(self) -> str:
        """Analyzer description."""
        return "Analyzes code complexity (cyclomatic, nested depth, etc.)"

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze code complexity.

        Args:
            code: Source code to analyze
            file_path: Path to the file

        Returns:
            List of complexity issues
        """
        issues = []

        # Parse code
        tree = ASTAnalyzer.parse_code(code)
        if tree is None:
            return issues

        # Check function complexity
        issues.extend(self._check_function_complexity(tree, file_path))

        # Check nesting depth
        issues.extend(self._check_nesting_depth(tree, file_path))

        # Check method complexity in classes
        issues.extend(self._check_method_complexity(tree, file_path))

        return issues

    def _calculate_cyclomatic_complexity(self, func_node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function.

        Args:
            func_node: Function AST node

        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            # Count decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # Each 'and' or 'or' adds complexity
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Try):
                # Count except handlers
                complexity += len(node.handlers)
            elif isinstance(node, (ast.ExceptHandler,)):
                complexity += 1

        return complexity

    def _check_function_complexity(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check function complexity.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        for func in ASTAnalyzer.get_functions(tree):
            complexity = self._calculate_cyclomatic_complexity(func)

            if complexity > self.max_complexity:
                issues.append(
                    CodeIssue(
                        issue_type="complexity",
                        severity="high" if complexity > 15 else "medium",
                        location=self._format_location(file_path, func.lineno),
                        message=f"Function '{func.name}' is too complex (CC: {complexity})",
                        suggestion=(
                            "Refactor into smaller functions or reduce conditional branches"
                        ),
                    )
                )

        return issues

    def _check_nesting_depth(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check nesting depth.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []
        max_depth = 0
        max_depth_node = None

        for func in ASTAnalyzer.get_functions(tree):
            depth, node = self._get_max_nesting_depth(func)

            if depth > 4:  # Threshold for nesting depth
                issues.append(
                    CodeIssue(
                        issue_type="complexity",
                        severity="medium",
                        location=self._format_location(file_path, func.lineno),
                        message=f"Function '{func.name}' has deep nesting (depth: {depth})",
                        suggestion="Reduce nesting by extracting nested logic to separate functions",
                    )
                )

        return issues

    def _get_max_nesting_depth(self, node: ast.AST, depth: int = 0) -> tuple:
        """Get maximum nesting depth.

        Args:
            node: AST node
            depth: Current depth

        Returns:
            Tuple of (max_depth, deepest_node)
        """
        max_depth = depth
        deepest_node = node

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth, child_node = self._get_max_nesting_depth(child, depth + 1)
                if child_depth > max_depth:
                    max_depth = child_depth
                    deepest_node = child_node

        return max_depth, deepest_node

    def _check_method_complexity(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Check method complexity in classes.

        Args:
            tree: AST tree
            file_path: File path

        Returns:
            List of issues
        """
        issues = []

        for cls in ASTAnalyzer.get_classes(tree):
            # Get methods directly from class body
            for item in cls.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic_complexity(item)

                    if complexity > self.max_complexity:
                        issues.append(
                            CodeIssue(
                                issue_type="complexity",
                                severity="high" if complexity > 15 else "medium",
                                location=self._format_location(
                                    file_path, item.lineno
                                ),
                                message=(
                                    f"Method '{cls.name}.{item.name}' is too complex (CC: {complexity})"
                                ),
                                suggestion=(
                                    "Refactor method into smaller functions or reduce branches"
                                ),
                            )
                        )

        return issues
