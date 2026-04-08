"""Tests for analyzer and metrics modules."""

import pytest

from socratic_analyzer.analyzer import AnalysisResult, CodeAnalyzer, CodeMetadata
from socratic_analyzer.metrics import MetricsCalculator, QualityMetrics


class TestCodeMetadata:
    """Test CodeMetadata model."""

    def test_metadata_creation(self):
        """Test creating code metadata."""
        metadata = CodeMetadata(
            language="python",
            lines_of_code=100,
            complexity="medium",
            has_tests=True,
            has_documentation=True,
        )

        assert metadata.language == "python"
        assert metadata.lines_of_code == 100
        assert metadata.complexity == "medium"
        assert metadata.has_tests is True
        assert metadata.has_documentation is True

    def test_metadata_defaults(self):
        """Test CodeMetadata default values."""
        metadata = CodeMetadata(language="javascript")

        assert metadata.lines_of_code == 0
        assert metadata.complexity == "low"
        assert metadata.has_tests is False
        assert metadata.has_documentation is False


class TestAnalysisResult:
    """Test AnalysisResult model."""

    def test_analysis_result_creation(self):
        """Test creating analysis result."""
        result = AnalysisResult(
            code_snippet="x = 1",
            language="python",
            issues=["Issue 1"],
            improvements=["Improve 1"],
            complexity_score=0.5,
            quality_score=0.8,
        )

        assert result.code_snippet == "x = 1"
        assert result.language == "python"
        assert len(result.issues) == 1
        assert result.complexity_score == 0.5

    def test_analysis_result_defaults(self):
        """Test AnalysisResult default values."""
        result = AnalysisResult(
            code_snippet="code",
            language="python",
        )

        assert result.issues == []
        assert result.improvements == []
        assert result.security_concerns == []
        assert result.performance_concerns == []
        assert result.recommendations == []
        assert result.complexity_score == 0.0
        assert result.quality_score == 0.0


class TestCodeAnalyzer:
    """Test CodeAnalyzer class."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = CodeAnalyzer()
        assert analyzer is not None

    def test_analyze_simple_code(self):
        """Test analyzing simple code."""
        analyzer = CodeAnalyzer()
        code = "x = 1\nprint(x)"
        result = analyzer.analyze(code, "python")

        assert result.code_snippet == code
        assert result.language == "python"
        assert isinstance(result.quality_score, float)
        assert isinstance(result.complexity_score, float)

    def test_analyze_with_default_language(self):
        """Test analyze uses python as default language."""
        analyzer = CodeAnalyzer()
        code = "x = 1"
        result = analyzer.analyze(code)

        assert result.language == "python"

    def test_analyze_batch(self):
        """Test analyzing multiple code snippets."""
        analyzer = CodeAnalyzer()
        snippets = [
            ("x = 1", "python"),
            ("const x = 1;", "javascript"),
            ("int x = 1;", "java"),
        ]

        results = analyzer.analyze_batch(snippets)

        assert len(results) == 3
        assert results[0].language == "python"
        assert results[1].language == "javascript"
        assert results[2].language == "java"

    def test_analyze_batch_empty(self):
        """Test analyzing empty batch."""
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_batch([])

        assert results == []

    def test_check_security(self):
        """Test security check method."""
        analyzer = CodeAnalyzer()
        code = "import os\nos.system('command')"
        concerns = analyzer.check_security(code, "python")

        assert isinstance(concerns, list)

    def test_check_performance(self):
        """Test performance check method."""
        analyzer = CodeAnalyzer()
        code = "for i in range(1000000):\n    for j in range(1000000):\n        pass"
        concerns = analyzer.check_performance(code, "python")

        assert isinstance(concerns, list)

    def test_analyze_empty_code(self):
        """Test analyzing empty code."""
        analyzer = CodeAnalyzer()
        result = analyzer.analyze("", "python")

        assert result.code_snippet == ""
        assert result.language == "python"


class TestQualityMetrics:
    """Test QualityMetrics model."""

    def test_metrics_creation(self):
        """Test creating quality metrics."""
        metrics = QualityMetrics(
            complexity_score=0.5,
            maintainability_index=75.0,
            test_coverage=80.0,
            security_score=0.9,
            performance_score=0.8,
            documentation_score=0.7,
            overall_quality=0.8,
        )

        assert metrics.complexity_score == 0.5
        assert metrics.maintainability_index == 75.0
        assert metrics.test_coverage == 80.0
        assert metrics.overall_quality == 0.8

    def test_metrics_defaults(self):
        """Test QualityMetrics default values."""
        metrics = QualityMetrics()

        assert metrics.complexity_score == 0.0
        assert metrics.maintainability_index == 0.0
        assert metrics.test_coverage == 0.0
        assert metrics.overall_quality == 0.0


class TestMetricsCalculator:
    """Test MetricsCalculator class."""

    def test_calculate_complexity_simple(self):
        """Test calculating complexity for simple code."""
        code = "x = 1"
        complexity = MetricsCalculator.calculate_complexity(code)

        assert isinstance(complexity, float)
        assert 0.0 <= complexity <= 1.0

    def test_calculate_complexity_with_control_flow(self):
        """Test complexity calculation with control flow."""
        code = "if x:\n    if y:\n        if z:\n            pass"
        complexity = MetricsCalculator.calculate_complexity(code)

        assert complexity > 0.0

    def test_calculate_complexity_empty_code(self):
        """Test complexity for empty code."""
        complexity = MetricsCalculator.calculate_complexity("")

        assert complexity == 0.0

    def test_calculate_complexity_normalized(self):
        """Test that complexity is normalized to 0-1."""
        code = "if a: pass\nif b: pass\nif c: pass\n" * 100
        complexity = MetricsCalculator.calculate_complexity(code)

        assert 0.0 <= complexity <= 1.0

    def test_calculate_maintainability_simple(self):
        """Test calculating maintainability."""
        code = "x = 1\ny = 2"
        maintainability = MetricsCalculator.calculate_maintainability(code)

        assert isinstance(maintainability, float)
        assert 0.0 <= maintainability <= 100.0

    def test_calculate_maintainability_with_documentation(self):
        """Test maintainability with comments and docstrings."""
        code = '"""\nDocstring\n"""\n# Comment\nx = 1'
        maintainability = MetricsCalculator.calculate_maintainability(code)

        assert maintainability > 0.0

    def test_calculate_maintainability_empty_code(self):
        """Test maintainability for empty code."""
        maintainability = MetricsCalculator.calculate_maintainability("")

        assert maintainability >= 99.0  # Allow for rounding

    def test_calculate_security_score_no_issues(self):
        """Test security score with no issues."""
        score = MetricsCalculator.calculate_security_score(0)

        assert score == 1.0

    def test_calculate_security_score_with_issues(self):
        """Test security score with issues."""
        score = MetricsCalculator.calculate_security_score(1)

        assert 0.0 <= score < 1.0

    def test_calculate_security_score_many_issues(self):
        """Test security score with many issues."""
        score = MetricsCalculator.calculate_security_score(10)

        assert score == 0.0

    def test_calculate_overall_quality(self):
        """Test overall quality calculation."""
        overall = MetricsCalculator.calculate_overall_quality(
            complexity=0.5,
            maintainability=75.0,
            security=0.9,
            performance=0.8,
            documentation=0.7,
        )

        assert isinstance(overall, float)
        assert 0.0 <= overall <= 1.0

    def test_calculate_overall_quality_perfect(self):
        """Test overall quality with perfect scores."""
        overall = MetricsCalculator.calculate_overall_quality(
            complexity=0.0,  # Low complexity is good
            maintainability=100.0,
            security=1.0,
            performance=1.0,
            documentation=1.0,
        )

        assert overall > 0.9

    def test_calculate_overall_quality_poor(self):
        """Test overall quality with poor scores."""
        overall = MetricsCalculator.calculate_overall_quality(
            complexity=1.0,  # High complexity is bad
            maintainability=0.0,
            security=0.0,
            performance=0.0,
            documentation=0.0,
        )

        assert overall < 0.2

    def test_calculate_metrics_simple_code(self):
        """Test calculating all metrics for simple code."""
        code = "x = 1\nprint(x)"
        metrics = MetricsCalculator.calculate_metrics(code)

        assert isinstance(metrics, QualityMetrics)
        assert metrics.complexity_score >= 0.0
        assert metrics.maintainability_index >= 0.0
        assert metrics.security_score >= 0.0

    def test_calculate_metrics_with_issues(self):
        """Test metrics with security and performance issues."""
        code = "x = 1"
        metrics = MetricsCalculator.calculate_metrics(
            code,
            security_issues=2,
            performance_issues=1,
            test_coverage=50.0,
            documentation_present=True,
        )

        assert metrics.security_score < 1.0
        assert metrics.performance_score < 1.0
        assert metrics.test_coverage == 50.0
        assert metrics.documentation_score == 0.8

    def test_calculate_metrics_no_issues(self):
        """Test metrics with no issues."""
        code = 'def foo():\n    """Docstring."""\n    return 1'
        metrics = MetricsCalculator.calculate_metrics(
            code,
            security_issues=0,
            performance_issues=0,
            test_coverage=100.0,
            documentation_present=True,
        )

        assert metrics.security_score == 1.0
        assert metrics.documentation_score == 0.8

    def test_calculate_metrics_no_documentation(self):
        """Test metrics without documentation."""
        code = "x = 1"
        metrics = MetricsCalculator.calculate_metrics(code, documentation_present=False)

        assert metrics.documentation_score == 0.3

    def test_calculate_metrics_empty_code(self):
        """Test metrics for empty code."""
        metrics = MetricsCalculator.calculate_metrics("")

        assert metrics.complexity_score == 0.0
        assert metrics.maintainability_index >= 99.0  # Allow for rounding
