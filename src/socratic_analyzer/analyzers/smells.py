"""Code smell detection for identifying code quality issues."""

import ast
from typing import List

from socratic_analyzer.models import CodeIssue
from socratic_analyzer.analyzers.base import BaseAnalyzer


class CodeSmellDetector(BaseAnalyzer):
    """Detect code smells and quality issues."""

    def __init__(self, max_method_length: int = 50, max_params: int = 5):
        """Initialize detector.

        Args:
            max_method_length: Maximum method length (lines)
            max_params: Maximum number of parameters
        """
        self.max_method_length = max_method_length
        self.max_params = max_params

    @property
    def name(self) -> str:
        """Analyzer name."""
        return "Code Smell Detector"

    @property
    def description(self) -> str:
        """Analyzer description."""
        return "Detects code smells and common quality issues"

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze code for smells.

        Args:
            code: Source code to analyze
            file_path: Path to file (for location reporting)

        Returns:
            List of CodeIssue objects for smells found
        """
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        # Run smell detections
        issues.extend(self._detect_long_methods(code, file_path, tree))
        issues.extend(self._detect_too_many_parameters(file_path, tree))
        issues.extend(self._detect_duplicate_code(code, file_path, tree))
        issues.extend(self._detect_global_variables(file_path, tree))
        issues.extend(self._detect_magic_numbers(code, file_path, tree))
        issues.extend(self._detect_broad_exception_handling(file_path, tree))
        issues.extend(self._detect_mutable_default_arguments(file_path, tree))
        issues.extend(self._detect_god_classes(file_path, tree))

        return issues

    def _detect_long_methods(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect methods that are too long.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for long methods
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Calculate method length
            method_lines = node.end_lineno - node.lineno + 1

            if method_lines > self.max_method_length:
                issues.append(
                    CodeIssue(
                        issue_type="smell",
                        severity="medium",
                        message=f"Method '{node.name}' is too long ({method_lines} lines)",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Consider breaking into smaller methods",
                    )
                )

        return issues

    def _detect_too_many_parameters(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect functions with too many parameters.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for too many parameters
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Count parameters (excluding self/cls)
            params = [arg.arg for arg in node.args.args if arg.arg not in ("self", "cls")]
            param_count = len(params)

            if param_count > self.max_params:
                issues.append(
                    CodeIssue(
                        issue_type="smell",
                        severity="medium",
                        message=f"Function '{node.name}' has too many parameters ({param_count})",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Consider using a data class or dict to group related parameters",
                    )
                )

        return issues

    def _detect_duplicate_code(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect duplicate code blocks.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for duplicate code
        """
        issues = []
        lines = code.split("\n")
        seen_blocks: dict = {}

        # Check for duplicate code blocks (simple heuristic)
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith("#"):
                continue

            # Check if we've seen this line before
            if stripped in seen_blocks:
                if i - seen_blocks[stripped][-1] > 10:  # Not consecutive
                    seen_blocks[stripped].append(i)
                    if len(seen_blocks[stripped]) > 1:
                        issues.append(
                            CodeIssue(
                                issue_type="smell",
                                severity="low",
                                message=f"Duplicate code detected at line {i+1}",
                                location=self._format_location(file_path, i + 1),
                                suggestion="Consider extracting to a shared function",
                            )
                        )
            else:
                seen_blocks[stripped] = [i]

        return issues

    def _detect_global_variables(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect global variable usage.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for global variables
        """
        issues = []

        # Get module-level assignments
        module_vars = set()
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        module_vars.add(target.id)

        # Check for use of global keyword
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                for name in node.names:
                    if name in module_vars:
                        issues.append(
                            CodeIssue(
                                issue_type="smell",
                                severity="high",
                                message=f"Global variable '{name}' used",
                                location=self._format_location(
                                    file_path, getattr(node, "lineno", 1)
                                ),
                                suggestion="Consider using function parameters or class attributes",
                            )
                        )

        return issues

    def _detect_magic_numbers(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect magic numbers without explanation.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for magic numbers
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip common magic numbers and constants
                if node.value in (0, 1, -1, 2, 10, 100, 1000, 60, 24, 365):
                    continue

                # Report other magic numbers
                issues.append(
                    CodeIssue(
                        issue_type="smell",
                        severity="low",
                        message=f"Magic number {node.value} without explanation",
                        location=self._format_location(
                            file_path, getattr(node, "lineno", 1)
                        ),
                        suggestion="Define as named constant for clarity",
                    )
                )
                # Limit reporting to avoid noise
                if len(issues) > 5:
                    break

        return issues

    def _detect_broad_exception_handling(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect overly broad exception handling.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for broad exceptions
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue

            # Check for bare except or Exception
            if node.type is None:
                issues.append(
                    CodeIssue(
                        issue_type="smell",
                        severity="high",
                        message="Bare 'except:' clause catches all exceptions",
                        location=self._format_location(
                            file_path, getattr(node, "lineno", 1)
                        ),
                        suggestion="Specify the exception type to catch",
                    )
                )
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                issues.append(
                    CodeIssue(
                        issue_type="smell",
                        severity="medium",
                        message="Catching 'Exception' is too broad",
                        location=self._format_location(
                            file_path, getattr(node, "lineno", 1)
                        ),
                        suggestion="Catch specific exception types",
                    )
                )

        return issues

    def _detect_mutable_default_arguments(
        self, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect mutable default arguments.

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for mutable defaults
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Check default arguments
            defaults = node.args.defaults + node.args.kw_defaults

            for default in defaults:
                if default is None:
                    continue

                # Check for list or dict literals
                if isinstance(default, (ast.List, ast.Dict)):
                    param_idx = len(node.args.args) - len(node.args.defaults)
                    param_name = node.args.args[param_idx].arg
                    issues.append(
                        CodeIssue(
                            issue_type="smell",
                            severity="high",
                            message=f"Mutable default argument '{param_name}' in function '{node.name}'",
                            location=self._format_location(file_path, node.lineno),
                            suggestion="Use None and initialize inside function",
                        )
                    )

        return issues

    def _detect_god_classes(self, file_path: str, tree: ast.AST) -> List[CodeIssue]:
        """Detect god classes (too many responsibilities).

        Args:
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for god classes
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Count methods and attributes
            methods = [item for item in node.body if isinstance(item, ast.FunctionDef)]
            method_count = len(methods)

            if method_count > 20:
                issues.append(
                    CodeIssue(
                        issue_type="smell",
                        severity="medium",
                        message=f"Class '{node.name}' has too many methods ({method_count})",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Consider splitting into smaller classes (Single Responsibility Principle)",
                    )
                )

        return issues
