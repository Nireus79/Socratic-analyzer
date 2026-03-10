"""Tests for data models."""

import pytest
from datetime import datetime, timezone

from socratic_analyzer import (
    Analysis,
    AnalyzerConfig,
    CodeIssue,
    MetricResult,
    ProjectAnalysis,
    ConfigurationError,
)


class TestCodeIssue:
    """Test CodeIssue model."""

    def test_create_issue(self) -> None:
        """Test creating a code issue."""
        issue = CodeIssue(
            issue_type="complexity",
            severity="high",
            location="file.py:42",
            message="Function is too complex",
            suggestion="Refactor into smaller functions",
        )

        assert issue.issue_type == "complexity"
        assert issue.severity == "high"
        assert issue.location == "file.py:42"
        assert issue.message == "Function is too complex"
        assert issue.suggestion == "Refactor into smaller functions"

    def test_issue_string_representation(self) -> None:
        """Test string representation of issue."""
        issue = CodeIssue(
            issue_type="style",
            severity="medium",
            location="main.py:10",
            message="Line too long",
        )

        str_repr = str(issue)
        assert "MEDIUM" in str_repr
        assert "main.py:10" in str_repr
        assert "Line too long" in str_repr


class TestMetricResult:
    """Test MetricResult model."""

    def test_create_metric(self) -> None:
        """Test creating a metric result."""
        metric = MetricResult(
            name="cyclomatic_complexity",
            value=8.5,
            threshold=10.0,
            status="ok",
        )

        assert metric.name == "cyclomatic_complexity"
        assert metric.value == 8.5
        assert metric.threshold == 10.0
        assert metric.status == "ok"

    def test_metric_with_warning(self) -> None:
        """Test metric with warning status."""
        metric = MetricResult(
            name="maintainability_index",
            value=45.0,
            threshold=50.0,
            status="warning",
        )

        assert metric.status == "warning"
        assert metric.value < metric.threshold

    def test_metric_string_representation(self) -> None:
        """Test string representation of metric."""
        metric = MetricResult(
            name="lines_of_code",
            value=150,
            status="info",
        )

        str_repr = str(metric)
        assert "lines_of_code" in str_repr
        assert "150" in str_repr


class TestAnalysis:
    """Test Analysis model."""

    def test_create_analysis(self) -> None:
        """Test creating an analysis."""
        issues = [
            CodeIssue(
                issue_type="style",
                severity="low",
                location="test.py:5",
                message="Unused variable",
            )
        ]

        analysis = Analysis(
            file_path="test.py",
            file_size=1024,
            language="python",
            issues=issues,
        )

        assert analysis.file_path == "test.py"
        assert analysis.file_size == 1024
        assert analysis.language == "python"
        assert analysis.total_issues == 1

    def test_analysis_critical_issues_count(self) -> None:
        """Test counting critical issues."""
        issues = [
            CodeIssue(
                issue_type="security",
                severity="critical",
                location="app.py:1",
                message="Issue 1",
            ),
            CodeIssue(
                issue_type="security",
                severity="critical",
                location="app.py:2",
                message="Issue 2",
            ),
            CodeIssue(
                issue_type="style",
                severity="low",
                location="app.py:3",
                message="Issue 3",
            ),
        ]

        analysis = Analysis(
            file_path="app.py",
            file_size=2048,
            language="python",
            issues=issues,
        )

        assert analysis.critical_issues == 2
        assert analysis.high_issues == 0
        assert analysis.total_issues == 3

    def test_analysis_timestamp(self) -> None:
        """Test that analysis has a timestamp."""
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
        )

        assert analysis.timestamp is not None
        assert isinstance(analysis.timestamp, datetime)
        # Check timezone is UTC
        assert analysis.timestamp.tzinfo == timezone.utc


class TestProjectAnalysis:
    """Test ProjectAnalysis model."""

    def test_create_project_analysis(self) -> None:
        """Test creating a project analysis."""
        analysis1 = Analysis(
            file_path="module1.py",
            file_size=1024,
            language="python",
        )

        analysis2 = Analysis(
            file_path="module2.py",
            file_size=2048,
            language="python",
        )

        project_analysis = ProjectAnalysis(
            project_path="/project",
            files_analyzed=2,
            analyses=[analysis1, analysis2],
        )

        assert project_analysis.project_path == "/project"
        assert project_analysis.files_analyzed == 2
        assert len(project_analysis.analyses) == 2

    def test_project_analysis_aggregates_issues(self) -> None:
        """Test that project analysis aggregates issues."""
        issues1 = [
            CodeIssue(
                issue_type="style",
                severity="critical",
                location="file1.py:1",
                message="Issue 1",
            ),
            CodeIssue(
                issue_type="style",
                severity="high",
                location="file1.py:2",
                message="Issue 2",
            ),
        ]

        issues2 = [
            CodeIssue(
                issue_type="style",
                severity="critical",
                location="file2.py:1",
                message="Issue 3",
            ),
        ]

        analysis1 = Analysis(
            file_path="file1.py",
            file_size=1000,
            language="python",
            issues=issues1,
        )

        analysis2 = Analysis(
            file_path="file2.py",
            file_size=2000,
            language="python",
            issues=issues2,
        )

        project = ProjectAnalysis(
            project_path="/project",
            files_analyzed=2,
            analyses=[analysis1, analysis2],
        )

        assert project.total_issues == 3
        assert project.critical_issues == 2
        assert project.high_issues == 1

    def test_project_analysis_overall_score(self) -> None:
        """Test overall quality score calculation."""
        # No issues = perfect score
        analysis_clean = Analysis(
            file_path="clean.py",
            file_size=1000,
            language="python",
            issues=[],
        )

        project_clean = ProjectAnalysis(
            project_path="/project",
            files_analyzed=1,
            analyses=[analysis_clean],
        )

        assert project_clean.overall_score == 100.0

    def test_project_analysis_recommendations(self) -> None:
        """Test recommendation generation."""
        issues = [
            CodeIssue(
                issue_type="security",
                severity="critical",
                location="app.py:1",
                message="Critical issue",
            ),
            CodeIssue(
                issue_type="style",
                severity="critical",
                location="app.py:2",
                message="Another critical issue",
            ),
        ]

        analysis = Analysis(
            file_path="app.py",
            file_size=1000,
            language="python",
            issues=issues,
        )

        project = ProjectAnalysis(
            project_path="/project",
            files_analyzed=1,
            analyses=[analysis],
        )

        recommendations = project.recommendations
        assert len(recommendations) > 0
        assert any("critical" in r.lower() for r in recommendations)


class TestAnalyzerConfig:
    """Test AnalyzerConfig model."""

    def test_create_config(self) -> None:
        """Test creating analyzer configuration."""
        config = AnalyzerConfig(
            analyze_types=True,
            analyze_docstrings=False,
            max_complexity=15,
            max_line_length=100,
        )

        assert config.analyze_types is True
        assert config.analyze_docstrings is False
        assert config.max_complexity == 15
        assert config.max_line_length == 100

    def test_config_default_values(self) -> None:
        """Test default configuration values."""
        config = AnalyzerConfig()

        assert config.analyze_types is True
        assert config.analyze_docstrings is True
        assert config.analyze_security is True
        assert config.analyze_performance is True
        assert config.max_complexity == 10
        assert config.max_line_length == 120
        assert config.use_llm is False

    def test_config_validation_max_complexity(self) -> None:
        """Test validation of max_complexity."""
        with pytest.raises(ValueError, match="max_complexity must be positive"):
            AnalyzerConfig(max_complexity=0)

        with pytest.raises(ValueError, match="max_complexity must be positive"):
            AnalyzerConfig(max_complexity=-5)

    def test_config_validation_max_line_length(self) -> None:
        """Test validation of max_line_length."""
        with pytest.raises(ValueError, match="max_line_length must be positive"):
            AnalyzerConfig(max_line_length=0)

    def test_config_validation_min_docstring_length(self) -> None:
        """Test validation of min_docstring_length."""
        with pytest.raises(ValueError, match="min_docstring_length must be non-negative"):
            AnalyzerConfig(min_docstring_length=-1)

        # Should allow 0
        config = AnalyzerConfig(min_docstring_length=0)
        assert config.min_docstring_length == 0

    def test_config_string_representation(self) -> None:
        """Test string representation of config."""
        config = AnalyzerConfig(
            max_complexity=12,
            max_line_length=110,
            use_llm=True,
        )

        str_repr = str(config)
        assert "complexity=12" in str_repr
        assert "line_length=110" in str_repr
        assert "llm=True" in str_repr
