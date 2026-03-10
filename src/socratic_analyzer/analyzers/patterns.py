"""Pattern analysis for code anti-patterns and design pattern detection."""

import ast
from typing import List, Set, Dict, Tuple

from socratic_analyzer.models import CodeIssue
from socratic_analyzer.analyzers.base import BaseAnalyzer


class PatternAnalyzer(BaseAnalyzer):
    """Detect code patterns, anti-patterns, and design patterns."""

    @property
    def name(self) -> str:
        """Analyzer name."""
        return "Pattern Analyzer"

    @property
    def description(self) -> str:
        """Analyzer description."""
        return "Detects code patterns, anti-patterns, and design patterns"

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze code for patterns.

        Args:
            code: Source code to analyze
            file_path: Path to file (for location reporting)

        Returns:
            List of CodeIssue objects for patterns found
        """
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        # Run pattern detections
        issues.extend(self._detect_singleton_pattern(code, file_path, tree))
        issues.extend(self._detect_factory_pattern(code, file_path, tree))
        issues.extend(self._detect_decorator_pattern(code, file_path, tree))
        issues.extend(self._detect_context_manager_pattern(code, file_path, tree))
        issues.extend(self._detect_callback_pattern(code, file_path, tree))
        issues.extend(self._detect_observer_pattern(code, file_path, tree))
        issues.extend(self._detect_strategy_pattern(code, file_path, tree))
        issues.extend(self._detect_template_method_pattern(code, file_path, tree))

        return issues

    def _detect_singleton_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Singleton pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for singleton patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Check for singleton pattern: class with private __init__ or metaclass
            has_private_init = False
            has_instance_var = False
            has_get_instance = False

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name == "__init__" and self._is_private_method(item):
                        has_private_init = True
                    if item.name == "get_instance":
                        has_get_instance = True
                elif isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if "_instance" in target.id or "instance" in target.id:
                                has_instance_var = True

            # Detect singleton pattern
            if (has_private_init or has_instance_var) and has_get_instance:
                issues.append(
                    CodeIssue(
                        issue_type="pattern",
                        severity="info",
                        message=f"Singleton pattern detected in class '{node.name}'",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Consider if Singleton is necessary; use dependency injection when possible",
                    )
                )

        return issues

    def _detect_factory_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Factory pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for factory patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Check for factory pattern: function that returns instances based on parameters
            returns_objects = False
            has_conditional_logic = False

            for item in ast.walk(node):
                if isinstance(item, ast.Return) and item.value:
                    if isinstance(item.value, ast.Call):
                        returns_objects = True
                elif isinstance(item, ast.If) or (hasattr(ast, 'Match') and isinstance(item, ast.Match)):
                    has_conditional_logic = True

            if returns_objects and has_conditional_logic and node.name.endswith(
                ("factory", "create", "build")
            ):
                issues.append(
                    CodeIssue(
                        issue_type="pattern",
                        severity="info",
                        message=f"Factory pattern detected in function '{node.name}'",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Factory pattern is a good design pattern; consider documenting it",
                    )
                )

        return issues

    def _detect_decorator_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Decorator pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for decorator patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Check for decorator pattern: class with __init__ taking wrapped object
            has_wrapped_param = False
            has_delegate_methods = False

            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    args = [arg.arg for arg in item.args.args if arg.arg != "self"]
                    if any(
                        "wrap" in arg or "obj" in arg or "component" in arg
                        for arg in args
                    ):
                        has_wrapped_param = True

                elif isinstance(item, ast.FunctionDef) and not item.name.startswith(
                    "_"
                ):
                    # Check if delegates to wrapped object
                    for child in ast.walk(item):
                        if isinstance(child, ast.Attribute):
                            if hasattr(child, "value") and isinstance(
                                child.value, ast.Name
                            ):
                                if child.value.id in ("wrapped", "component", "obj"):
                                    has_delegate_methods = True

            if has_wrapped_param and has_delegate_methods:
                issues.append(
                    CodeIssue(
                        issue_type="pattern",
                        severity="info",
                        message=f"Decorator pattern detected in class '{node.name}'",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Decorator pattern is a good design pattern; ensure it's well documented",
                    )
                )

        return issues

    def _detect_context_manager_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Context Manager pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for context manager patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            has_enter = False
            has_exit = False

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name == "__enter__":
                        has_enter = True
                    elif item.name == "__exit__":
                        has_exit = True

            if has_enter and has_exit:
                issues.append(
                    CodeIssue(
                        issue_type="pattern",
                        severity="info",
                        message=f"Context Manager pattern detected in class '{node.name}'",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Context Manager pattern is good; ensure proper resource cleanup in __exit__",
                    )
                )

        return issues

    def _detect_callback_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Callback pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for callback patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Check for callback pattern: function that accepts callable parameter
            callable_params = []
            for arg in node.args.args:
                if "callback" in arg.arg or "handler" in arg.arg or "func" in arg.arg:
                    callable_params.append(arg.arg)

            # Check if callback is actually called
            if callable_params:
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id in callable_params:
                                issues.append(
                                    CodeIssue(
                                        issue_type="pattern",
                                        severity="info",
                                        message=f"Callback pattern detected in function '{node.name}'",
                                        location=self._format_location(
                                            file_path, node.lineno
                                        ),
                                        suggestion="Document expected callback signature and when it's called",
                                    )
                                )
                                break

        return issues

    def _detect_observer_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Observer pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for observer patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            has_attach = False
            has_detach = False
            has_notify = False

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if "attach" in item.name or "subscribe" in item.name:
                        has_attach = True
                    elif "detach" in item.name or "unsubscribe" in item.name:
                        has_detach = True
                    elif "notify" in item.name or "update" in item.name:
                        has_notify = True

            if (has_attach or has_detach) and has_notify:
                issues.append(
                    CodeIssue(
                        issue_type="pattern",
                        severity="info",
                        message=f"Observer pattern detected in class '{node.name}'",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Observer pattern is good; ensure thread-safety in multi-threaded contexts",
                    )
                )

        return issues

    def _detect_strategy_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Strategy pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for strategy patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Check for strategy pattern: class that takes strategy as parameter
            has_strategy_param = False
            uses_strategy = False

            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    args = [arg.arg for arg in item.args.args if arg.arg != "self"]
                    if any("strategy" in arg for arg in args):
                        has_strategy_param = True

                        # Check if strategy is used
                        for child in ast.walk(item):
                            if isinstance(child, ast.Attribute):
                                if hasattr(child, "value") and isinstance(
                                    child.value, ast.Name
                                ):
                                    if "strategy" in child.value.id:
                                        uses_strategy = True

            if has_strategy_param and uses_strategy:
                issues.append(
                    CodeIssue(
                        issue_type="pattern",
                        severity="info",
                        message=f"Strategy pattern detected in class '{node.name}'",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Strategy pattern is good; document available strategies",
                    )
                )

        return issues

    def _detect_template_method_pattern(
        self, code: str, file_path: str, tree: ast.AST
    ) -> List[CodeIssue]:
        """Detect Template Method pattern usage.

        Args:
            code: Source code
            file_path: File path
            tree: AST tree

        Returns:
            List of CodeIssue for template method patterns
        """
        issues = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Check for template method: base class with abstract/overridable methods
            has_template_method = False
            has_abstract_methods = False

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name.startswith("_") and not item.name.startswith("__"):
                        # Private method that might be overridden
                        has_template_method = True
                    if "NotImplementedError" in ast.unparse(item):
                        has_abstract_methods = True

            if has_template_method and has_abstract_methods:
                issues.append(
                    CodeIssue(
                        issue_type="pattern",
                        severity="info",
                        message=f"Template Method pattern detected in class '{node.name}'",
                        location=self._format_location(file_path, node.lineno),
                        suggestion="Template Method pattern is good; consider using ABC for clarity",
                    )
                )

        return issues

    @staticmethod
    def _is_private_method(node: ast.FunctionDef) -> bool:
        """Check if method is private.

        Args:
            node: FunctionDef node

        Returns:
            True if method is private
        """
        return node.name.startswith("_") and not node.name.startswith("__")
