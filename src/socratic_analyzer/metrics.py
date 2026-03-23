"""
Code quality metrics calculation.
"""

import logging
from typing import Dict

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class QualityMetrics(BaseModel):
    """Code quality metrics."""

    complexity_score: float = Field(default=0.0, description="Complexity score (0-1)")
    maintainability_index: float = Field(default=0.0, description="Maintainability index (0-100)")
    test_coverage: float = Field(default=0.0, description="Test coverage percentage (0-100)")
    security_score: float = Field(default=0.0, description="Security score (0-1)")
    performance_score: float = Field(default=0.0, description="Performance score (0-1)")
    documentation_score: float = Field(default=0.0, description="Documentation score (0-1)")
    overall_quality: float = Field(default=0.0, description="Overall quality score (0-1)")


class MetricsCalculator:
    """
    Calculate code quality metrics.

    Provides methods to compute various metrics that measure code quality,
    complexity, maintainability, and other important properties.
    """

    @staticmethod
    def calculate_complexity(code: str) -> float:
        """
        Calculate cyclomatic complexity score.

        Args:
            code: Source code

        Returns:
            Complexity score (0-1, where 1 is most complex)
        """
        # Simple heuristic: count control flow statements
        control_flow_keywords = ["if", "else", "elif", "for", "while", "try", "except", "case"]
        keyword_count = sum(
            code.lower().count(keyword) for keyword in control_flow_keywords
        )
        lines = len(code.split("\n"))

        # Normalize to 0-1 range
        if lines == 0:
            return 0.0

        score = min(1.0, keyword_count / max(1, lines))
        return round(score, 2)

    @staticmethod
    def calculate_maintainability(code: str) -> float:
        """
        Calculate maintainability index.

        Args:
            code: Source code

        Returns:
            Maintainability index (0-100)
        """
        lines = len(code.split("\n"))
        comments = code.count("#")
        docstrings = code.count('"""') + code.count("'''")

        # Simple calculation: longer code with less documentation is less maintainable
        if lines == 0:
            return 100.0

        documentation_ratio = (comments + docstrings) / lines
        score = min(100.0, 100 - (lines / 10) + (documentation_ratio * 20))

        return round(max(0.0, score), 2)

    @staticmethod
    def calculate_security_score(issues_count: int) -> float:
        """
        Calculate security score based on identified issues.

        Args:
            issues_count: Number of security issues

        Returns:
            Security score (0-1, where 1 is most secure)
        """
        score = max(0.0, 1.0 - (issues_count * 0.2))
        return round(min(1.0, score), 2)

    @staticmethod
    def calculate_overall_quality(
        complexity: float,
        maintainability: float,
        security: float,
        performance: float,
        documentation: float
    ) -> float:
        """
        Calculate overall quality score.

        Args:
            complexity: Complexity score
            maintainability: Maintainability index (0-100)
            security: Security score
            performance: Performance score
            documentation: Documentation score

        Returns:
            Overall quality score (0-1)
        """
        # Normalize maintainability to 0-1
        maintainability_normalized = min(1.0, maintainability / 100.0)

        # Weight the scores
        weights = {
            "complexity": 0.15,
            "maintainability": 0.25,
            "security": 0.30,
            "performance": 0.15,
            "documentation": 0.15
        }

        # Lower complexity is better (invert the score)
        complexity_score = 1.0 - complexity

        overall = (
            complexity_score * weights["complexity"] +
            maintainability_normalized * weights["maintainability"] +
            security * weights["security"] +
            performance * weights["performance"] +
            documentation * weights["documentation"]
        )

        return round(overall, 2)

    @staticmethod
    def calculate_metrics(
        code: str,
        security_issues: int = 0,
        performance_issues: int = 0,
        test_coverage: float = 0.0,
        documentation_present: bool = False
    ) -> QualityMetrics:
        """
        Calculate all quality metrics for given code.

        Args:
            code: Source code
            security_issues: Number of security issues found
            performance_issues: Number of performance issues found
            test_coverage: Test coverage percentage
            documentation_present: Whether documentation exists

        Returns:
            Quality metrics object
        """
        complexity = MetricsCalculator.calculate_complexity(code)
        maintainability = MetricsCalculator.calculate_maintainability(code)
        security_score = MetricsCalculator.calculate_security_score(security_issues)
        performance_score = max(0.0, 1.0 - (performance_issues * 0.1))
        documentation_score = 0.8 if documentation_present else 0.3

        overall = MetricsCalculator.calculate_overall_quality(
            complexity,
            maintainability,
            security_score,
            performance_score,
            documentation_score
        )

        return QualityMetrics(
            complexity_score=complexity,
            maintainability_index=maintainability,
            test_coverage=test_coverage,
            security_score=security_score,
            performance_score=performance_score,
            documentation_score=documentation_score,
            overall_quality=overall
        )
