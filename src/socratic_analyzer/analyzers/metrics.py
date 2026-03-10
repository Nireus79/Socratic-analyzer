"""Code metrics analyzer."""

import ast
from typing import List

from socratic_analyzer.analyzers.base import BaseAnalyzer
from socratic_analyzer.models import CodeIssue, MetricResult
from socratic_analyzer.utils.ast_parser import ASTAnalyzer


class MetricsAnalyzer(BaseAnalyzer):
    """Calculate code metrics."""

    @property
    def name(self) -> str:
        """Analyzer name."""
        return "MetricsAnalyzer"

    @property
    def description(self) -> str:
        """Analyzer description."""
        return "Calculates code metrics (LOC, maintainability, etc.)"

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze code metrics.

        Args:
            code: Source code to analyze
            file_path: Path to the file

        Returns:
            Empty list (metrics are returned separately)
        """
        # This analyzer returns metrics, not issues
        return []

    def calculate_metrics(self, code: str) -> List[MetricResult]:
        """Calculate all code metrics.

        Args:
            code: Source code to analyze

        Returns:
            List of MetricResult objects
        """
        metrics = []

        # Lines of code metrics
        metrics.extend(self._calculate_loc_metrics(code))

        # Maintainability index
        metrics.extend(self._calculate_maintainability(code))

        # Function metrics
        metrics.extend(self._calculate_function_metrics(code))

        return metrics

    def _calculate_loc_metrics(self, code: str) -> List[MetricResult]:
        """Calculate lines of code metrics.

        Args:
            code: Source code

        Returns:
            List of metrics
        """
        metrics = []

        total_lines = len(code.split("\n"))
        code_lines = ASTAnalyzer.count_lines(code)
        blank_lines = ASTAnalyzer.count_blank_lines(code)

        metrics.append(
            MetricResult(
                name="total_lines",
                value=total_lines,
                description="Total lines in file",
            )
        )

        metrics.append(
            MetricResult(
                name="code_lines",
                value=code_lines,
                description="Non-empty, non-comment lines",
            )
        )

        metrics.append(
            MetricResult(
                name="blank_lines",
                value=blank_lines,
                description="Number of blank lines",
            )
        )

        if total_lines > 0:
            blank_ratio = (blank_lines / total_lines) * 100
            metrics.append(
                MetricResult(
                    name="blank_ratio",
                    value=blank_ratio,
                    threshold=30.0,
                    status="ok" if blank_ratio < 30 else "warning",
                    description="Percentage of blank lines",
                )
            )

        return metrics

    def _calculate_maintainability(self, code: str) -> List[MetricResult]:
        """Calculate maintainability index.

        Args:
            code: Source code

        Returns:
            List of metrics
        """
        metrics = []

        # Simple maintainability calculation
        # Based on: lines of code, cyclomatic complexity, Halstead metrics
        tree = ASTAnalyzer.parse_code(code)
        if tree is None:
            return metrics

        loc = ASTAnalyzer.count_lines(code)
        num_functions = len(ASTAnalyzer.get_functions(tree))
        num_classes = len(ASTAnalyzer.get_classes(tree))

        # Simplified maintainability index (0-100)
        # Higher is better
        if loc == 0:
            maintainability = 100.0
        else:
            # Factors:
            # - Fewer functions is good (more modular)
            # - Balanced LOC per function is good
            avg_loc_per_func = loc / max(1, num_functions)

            # Calculate score
            score = 100.0
            if avg_loc_per_func > 50:
                score -= 20
            elif avg_loc_per_func > 100:
                score -= 40

            if num_functions < 3:
                score -= 10
            if num_classes == 0 and num_functions > 0:
                score -= 5

            maintainability = max(10.0, min(100.0, score))

        metrics.append(
            MetricResult(
                name="maintainability_index",
                value=maintainability,
                threshold=70.0,
                status="ok" if maintainability >= 70 else "warning",
                description="Maintainability index (0-100, higher is better)",
            )
        )

        return metrics

    def _calculate_function_metrics(self, code: str) -> List[MetricResult]:
        """Calculate function-related metrics.

        Args:
            code: Source code

        Returns:
            List of metrics
        """
        metrics = []

        tree = ASTAnalyzer.parse_code(code)
        if tree is None:
            return metrics

        functions = ASTAnalyzer.get_functions(tree)
        classes = ASTAnalyzer.get_classes(tree)

        metrics.append(
            MetricResult(
                name="num_functions",
                value=len(functions),
                description="Number of functions defined",
            )
        )

        metrics.append(
            MetricResult(
                name="num_classes",
                value=len(classes),
                description="Number of classes defined",
            )
        )

        # Average function length
        if functions:
            func_lengths = []
            for func in functions:
                func_info = ASTAnalyzer.get_function_info(func)
                func_lengths.append(func_info["statements"])

            avg_length = sum(func_lengths) / len(func_lengths)
            metrics.append(
                MetricResult(
                    name="avg_function_length",
                    value=avg_length,
                    threshold=20.0,
                    status="ok" if avg_length < 20 else "warning",
                    description="Average function length (statements)",
                )
            )

        return metrics
