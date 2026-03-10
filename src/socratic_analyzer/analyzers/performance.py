"""Performance analysis for detecting performance anti-patterns."""

import ast
from typing import List

from socratic_analyzer.models import CodeIssue
from socratic_analyzer.analyzers.base import BaseAnalyzer


class PerformanceAnalyzer(BaseAnalyzer):
    """Detect performance anti-patterns and inefficient code."""

    @property
    def name(self) -> str:
        """Analyzer name."""
        return "Performance Analyzer"

    @property
    def description(self) -> str:
        """Analyzer description."""
        return "Detects performance anti-patterns and inefficient code"

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze code for performance issues.

        Args:
            code: Source code to analyze
            file_path: Path to file (for location reporting)

        Returns:
            List of CodeIssue objects for performance issues found
        """
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        # Run performance checks
        issues.extend(self._detect_string_concatenation_in_loop(file_path, tree))
        issues.extend(self._detect_list_operations_in_loop(file_path, tree))
        issues.extend(self._detect_repeated_function_calls(file_path, tree))
        issues.extend(self._detect_inefficient_list_operations(file_path, tree))
        issues.extend(self._detect_n_plus_one_patterns(file_path, tree))
        issues.extend(self._detect_unnecessary_list_comprehension(file_path, tree))
        issues.extend(self._detect_type_checking_in_hot_path(file_path, tree))

        return issues

    def _detect_string_concatenation_in_loop(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect string concatenation in loops (inefficient).

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for string concatenation in loops
        """
        issues = []

        for loop_node in ast.walk(tree):
            if not isinstance(loop_node, (ast.For, ast.While)):
                continue

            # Check for string concatenation in loop body
            for node in ast.walk(loop_node):
                if isinstance(node, ast.AugAssign):
                    if isinstance(node.op, ast.Add):
                        # Check if left side is string variable
                        if isinstance(node.target, ast.Name):
                            issues.append(
                                CodeIssue(
                                    issue_type="performance",
                                    severity="medium",
                                    message=f"String concatenation in loop (variable '{node.target.id}')",
                                    location=self._format_location(
                                        file_path, getattr(node, "lineno", 1)
                                    ),
                                    suggestion="Use list and join(), or io.StringIO for efficiency",
                                )
                            )

        return issues

    def _detect_list_operations_in_loop(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect inefficient list operations in loops.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for list operations in loops
        """
        issues = []

        for loop_node in ast.walk(tree):
            if not isinstance(loop_node, (ast.For, ast.While)):
                continue

            # Check for list.append, list.insert, list.remove in loop
            for node in ast.walk(loop_node):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ("insert", "remove", "pop"):
                            issues.append(
                                CodeIssue(
                                    issue_type="performance",
                                    severity="medium",
                                    message=f"Inefficient list.{node.func.attr}() in loop",
                                    location=self._format_location(
                                        file_path, getattr(node, "lineno", 1)
                                    ),
                                    suggestion="Avoid insert/remove in loops; use list comprehension or set",
                                )
                            )

        return issues

    def _detect_repeated_function_calls(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect repeated function calls that could be cached.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for repeated function calls
        """
        issues = []

        # Track function calls
        call_counts = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    call_name = ast.unparse(node.func)
                    call_counts[call_name] = call_counts.get(call_name, 0) + 1

        # Report repeated calls
        for call_name, count in call_counts.items():
            if count > 5 and any(
                method in call_name for method in ("len(", "str(", "type(", "isinstance(")
            ):
                issues.append(
                    CodeIssue(
                        issue_type="performance",
                        severity="low",
                        message=f"Function '{call_name}' called {count} times (possible caching opportunity)",
                        location=self._format_location(file_path, 1),
                        suggestion="Consider caching result if function is pure",
                    )
                )
                break  # Limit to one report

        return issues

    def _detect_inefficient_list_operations(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect inefficient list operations.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for inefficient operations
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # Check for list() constructor
                    if node.func.id == "list":
                        if node.args and isinstance(node.args[0], ast.Subscript):
                            issues.append(
                                CodeIssue(
                                    issue_type="performance",
                                    severity="low",
                                    message="Using list(slice) instead of slice directly",
                                    location=self._format_location(
                                        file_path, getattr(node, "lineno", 1)
                                    ),
                                    suggestion="Use slice notation directly instead of list()",
                                )
                            )

        return issues

    def _detect_n_plus_one_patterns(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect N+1 query pattern (conceptual).

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for N+1 patterns
        """
        issues = []

        # Look for loops with database operations
        for loop_node in ast.walk(tree):
            if not isinstance(loop_node, (ast.For, ast.While)):
                continue

            # Check for database-like calls
            for node in ast.walk(loop_node):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ("get", "fetch", "query", "select"):
                            issues.append(
                                CodeIssue(
                                    issue_type="performance",
                                    severity="high",
                                    message="Potential N+1 query pattern detected",
                                    location=self._format_location(
                                        file_path, getattr(node, "lineno", 1)
                                    ),
                                    suggestion="Fetch all data in one query, then filter in memory",
                                )
                            )
                            break

        return issues

    def _detect_unnecessary_list_comprehension(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect unnecessary list comprehensions.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for unnecessary comprehensions
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                # Check if comprehension just returns items unchanged
                if len(node.generators) == 1:
                    generator = node.generators[0]
                    # If element is just the variable, it's unnecessary
                    if isinstance(node.elt, ast.Name):
                        if isinstance(generator.target, ast.Name):
                            if node.elt.id == generator.target.id and not generator.ifs:
                                issues.append(
                                    CodeIssue(
                                        issue_type="performance",
                                        severity="low",
                                        message="Unnecessary list comprehension",
                                        location=self._format_location(
                                            file_path, getattr(node, "lineno", 1)
                                        ),
                                        suggestion="Use list() constructor instead",
                                    )
                                )

        return issues

    def _detect_type_checking_in_hot_path(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect type checking in hot paths.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for type checking in hot paths
        """
        issues = []

        for loop_node in ast.walk(tree):
            if not isinstance(loop_node, (ast.For, ast.While)):
                continue

            # Check for type() or isinstance() calls in loop
            for node in ast.walk(loop_node):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ("type", "isinstance"):
                            issues.append(
                                CodeIssue(
                                    issue_type="performance",
                                    severity="low",
                                    message=f"Type checking with {node.func.id}() in loop",
                                    location=self._format_location(
                                        file_path, getattr(node, "lineno", 1)
                                    ),
                                    suggestion="Move type check outside loop if possible",
                                )
                            )
                            break

        return issues
