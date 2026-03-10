"""Data models for Socratic Analyzer."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class CodeIssue:
    """Detected code issue."""

    issue_type: str  # "complexity", "style", "security", "performance", "maintenance"
    severity: str  # "critical", "high", "medium", "low", "info"
    location: str  # "file.py:123" or "module.function:456"
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.severity.upper()}: {self.location} - {self.message}"


@dataclass
class MetricResult:
    """Code quality metric result."""

    name: str  # "cyclomatic_complexity", "maintainability_index", etc.
    value: float
    threshold: Optional[float] = None
    status: str = "info"  # "ok", "warning", "critical"
    description: Optional[str] = None

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.name}: {self.value} (status: {self.status})"


@dataclass
class Analysis:
    """Complete code analysis for a single file."""

    file_path: str
    file_size: int
    language: str
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: List[MetricResult] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def critical_issues(self) -> int:
        """Count of critical issues."""
        return len([i for i in self.issues if i.severity == "critical"])

    @property
    def high_issues(self) -> int:
        """Count of high severity issues."""
        return len([i for i in self.issues if i.severity == "high"])

    @property
    def total_issues(self) -> int:
        """Total number of issues."""
        return len(self.issues)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Analysis({self.file_path}, issues={self.total_issues}, patterns={len(self.patterns)})"


@dataclass
class ProjectAnalysis:
    """Project-wide analysis aggregating multiple file analyses."""

    project_path: str
    files_analyzed: int
    analyses: List[Analysis] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_issues(self) -> int:
        """Total issues across all files."""
        return sum(a.total_issues for a in self.analyses)

    @property
    def critical_issues(self) -> int:
        """Total critical issues across all files."""
        return sum(a.critical_issues for a in self.analyses)

    @property
    def high_issues(self) -> int:
        """Total high severity issues across all files."""
        return sum(a.high_issues for a in self.analyses)

    @property
    def overall_score(self) -> float:
        """Overall quality score (0-100)."""
        if not self.analyses:
            return 100.0

        # Calculate score based on issues
        total_issues = self.total_issues
        critical_weight = 10
        high_weight = 5
        medium_weight = 2
        low_weight = 1

        weighted_issues = 0
        for analysis in self.analyses:
            for issue in analysis.issues:
                if issue.severity == "critical":
                    weighted_issues += critical_weight
                elif issue.severity == "high":
                    weighted_issues += high_weight
                elif issue.severity == "medium":
                    weighted_issues += medium_weight
                elif issue.severity == "low":
                    weighted_issues += low_weight

        # Scale: 100 - (weighted_issues / total_issues_possible) * 100
        # Cap the score between 0 and 100
        score = max(0.0, 100.0 - (weighted_issues / max(1, total_issues * 5)))
        return min(100.0, score)

    @property
    def recommendations(self) -> List[str]:
        """Get recommendations based on analysis."""
        recommendations = []

        if self.critical_issues > 0:
            recommendations.append(f"Fix {self.critical_issues} critical issue(s) immediately")

        if self.high_issues > 5:
            recommendations.append(f"Address {self.high_issues} high-severity issues")

        avg_issues = self.total_issues / max(1, self.files_analyzed)
        if avg_issues > 5:
            recommendations.append("High issue density - consider refactoring affected files")

        return recommendations

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"ProjectAnalysis({self.project_path}, "
            f"files={self.files_analyzed}, "
            f"issues={self.total_issues}, "
            f"score={self.overall_score:.1f})"
        )


@dataclass
class AnalyzerConfig:
    """Configuration for Socratic Analyzer."""

    # Analysis options
    analyze_types: bool = True  # Check type hints
    analyze_docstrings: bool = True  # Check documentation
    analyze_security: bool = True  # Check security issues
    analyze_performance: bool = True  # Check performance antipatterns
    analyze_patterns: bool = True  # Detect design patterns

    # Thresholds
    max_complexity: int = 10  # Max cyclomatic complexity
    max_line_length: int = 120  # Max line length
    min_docstring_length: int = 10  # Min docstring length

    # Output
    include_metrics: bool = True
    include_patterns: bool = True
    detailed_output: bool = False

    # Optional LLM analysis
    use_llm: bool = False
    llm_provider: str = "anthropic"
    llm_model: str = "claude-opus"

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.max_complexity <= 0:
            raise ValueError("max_complexity must be positive")
        if self.max_line_length <= 0:
            raise ValueError("max_line_length must be positive")
        if self.min_docstring_length < 0:
            raise ValueError("min_docstring_length must be non-negative")

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"AnalyzerConfig(complexity={self.max_complexity}, "
            f"line_length={self.max_line_length}, "
            f"llm={self.use_llm})"
        )
