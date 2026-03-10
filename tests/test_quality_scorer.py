"""Tests for quality scorer utility."""

import pytest

from socratic_analyzer.models import Analysis, CodeIssue, MetricResult
from socratic_analyzer.utils.quality_scorer import QualityScorer


class TestQualityScorer:
    """Test QualityScorer."""

    def test_perfect_score_no_issues(self) -> None:
        """Test perfect score with no issues."""
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=[],
            metrics=[],
            patterns=[],
        )
        score = QualityScorer.calculate_quality_score(analysis)
        assert score == 100.0

    def test_score_with_critical_issue(self) -> None:
        """Test score with critical issue."""
        issue = CodeIssue(
            issue_type="syntax",
            severity="critical",
            message="Syntax error",
            location="test.py:1",
        )
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=[issue],
            metrics=[],
            patterns=[],
        )
        score = QualityScorer.calculate_quality_score(analysis)
        assert score < 100.0
        assert score > 0.0

    def test_score_with_multiple_issues(self) -> None:
        """Test score with multiple issues."""
        issues = [
            CodeIssue(
                issue_type="complexity",
                severity="high",
                message="High complexity",
                location="test.py:1",
            ),
            CodeIssue(
                issue_type="style",
                severity="low",
                message="Style issue",
                location="test.py:2",
            ),
        ]
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=issues,
            metrics=[],
            patterns=[],
        )
        score = QualityScorer.calculate_quality_score(analysis)
        assert 0 <= score <= 100

    def test_quality_rating_excellent(self) -> None:
        """Test quality rating for excellent score."""
        rating = QualityScorer.get_quality_rating(95.0)
        assert rating == "Excellent"

    def test_quality_rating_very_good(self) -> None:
        """Test quality rating for very good score."""
        rating = QualityScorer.get_quality_rating(85.0)
        assert rating == "Very Good"

    def test_quality_rating_good(self) -> None:
        """Test quality rating for good score."""
        rating = QualityScorer.get_quality_rating(75.0)
        assert rating == "Good"

    def test_quality_rating_fair(self) -> None:
        """Test quality rating for fair score."""
        rating = QualityScorer.get_quality_rating(65.0)
        assert rating == "Fair"

    def test_quality_rating_poor(self) -> None:
        """Test quality rating for poor score."""
        rating = QualityScorer.get_quality_rating(55.0)
        assert rating == "Poor"

    def test_quality_rating_critical(self) -> None:
        """Test quality rating for critical score."""
        rating = QualityScorer.get_quality_rating(30.0)
        assert rating == "Critical"

    def test_quality_color_green(self) -> None:
        """Test color for excellent score."""
        color = QualityScorer.get_quality_color(95.0)
        assert color == "green"

    def test_quality_color_red(self) -> None:
        """Test color for critical score."""
        color = QualityScorer.get_quality_color(30.0)
        assert color == "red"

    def test_issue_score_calculation(self) -> None:
        """Test issue-based score calculation."""
        issues = [
            CodeIssue(
                issue_type="syntax",
                severity="critical",
                message="Syntax error",
                location="test.py:1",
            ),
        ]
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=issues,
            metrics=[],
            patterns=[],
        )
        score = QualityScorer.calculate_issue_score(analysis)
        assert score < 100.0

    def test_metrics_score_calculation(self) -> None:
        """Test metrics-based score calculation."""
        metrics = [
            MetricResult(
                name="lines_of_code",
                value=100.0,
                threshold=500.0,
                status="ok",
            ),
        ]
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=[],
            metrics=metrics,
            patterns=[],
        )
        score = QualityScorer.calculate_metrics_score(analysis)
        assert 0 <= score <= 100

    def test_improvement_suggestions_for_critical_code(self) -> None:
        """Test improvement suggestions for critical code."""
        issues = [
            CodeIssue(
                issue_type="syntax",
                severity="critical",
                message="Syntax error",
                location="test.py:1",
            ),
        ]
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=issues,
            metrics=[],
            patterns=[],
        )
        suggestions = QualityScorer.get_improvement_suggestions(analysis)
        assert len(suggestions) > 0
        assert any("critical" in s.lower() for s in suggestions)

    def test_quality_report_structure(self) -> None:
        """Test quality report structure."""
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=[],
            metrics=[],
            patterns=[],
        )
        report = QualityScorer.create_quality_report(analysis)

        # Check required fields
        assert "overall_score" in report
        assert "rating" in report
        assert "color" in report
        assert "issue_count" in report
        assert "suggestions" in report

    def test_quality_report_with_issues(self) -> None:
        """Test quality report with issues."""
        issues = [
            CodeIssue(
                issue_type="complexity",
                severity="high",
                message="High complexity",
                location="test.py:1",
            ),
            CodeIssue(
                issue_type="style",
                severity="low",
                message="Style issue",
                location="test.py:2",
            ),
        ]
        analysis = Analysis(
            file_path="test.py",
            file_size=100,
            language="python",
            issues=issues,
            metrics=[],
            patterns=[],
        )
        report = QualityScorer.create_quality_report(analysis)

        assert report["issue_count"] == 2
        assert report["high_issues"] == 1
        assert report["low_issues"] == 1
