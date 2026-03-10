"""Tests for analyzer client."""

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from socratic_analyzer import AnalyzerConfig, Analysis
from socratic_analyzer.async_client import AsyncAnalyzerClient
from socratic_analyzer.client import AnalyzerClient


class TestAnalyzerClient:
    """Test AnalyzerClient."""

    @pytest.fixture
    def client(self) -> AnalyzerClient:
        """Provide analyzer client."""
        return AnalyzerClient()

    @pytest.fixture
    def sample_code(self) -> str:
        """Sample Python code."""
        return '''
"""Module for testing."""

def calculate(x, y):
    """Calculate sum."""
    result = x + y
    return result


class Calculator:
    """Simple calculator."""

    def add(self, a, b):
        return a + b
'''

    def test_client_creation(self, client) -> None:
        """Test client creation."""
        assert client is not None
        assert client.config is not None

    def test_analyze_code(self, client, sample_code) -> None:
        """Test code analysis."""
        analysis = client.analyze_code(sample_code, "test.py")

        assert analysis is not None
        assert analysis.file_path == "test.py"
        assert analysis.language == "python"
        assert analysis.file_size > 0

    def test_analysis_has_issues(self, client) -> None:
        """Test that analysis detects issues."""
        code = """
def bad_function():
    pass
"""
        analysis = client.analyze_code(code, "test.py")

        assert len(analysis.issues) > 0

    def test_analysis_has_metrics(self, client, sample_code) -> None:
        """Test that analysis includes metrics."""
        analysis = client.analyze_code(sample_code, "test.py")

        assert len(analysis.metrics) > 0

    def test_analysis_has_patterns(self, client, sample_code) -> None:
        """Test that analysis detects patterns."""
        analysis = client.analyze_code(sample_code, "test.py")

        assert isinstance(analysis.patterns, list)

    def test_generate_text_report(self, client, sample_code) -> None:
        """Test text report generation."""
        analysis = client.analyze_code(sample_code, "test.py")
        report = client.generate_report(analysis, format="text")

        assert isinstance(report, str)
        assert "test.py" in report
        assert "SUMMARY" in report

    def test_generate_json_report(self, client, sample_code) -> None:
        """Test JSON report generation."""
        analysis = client.analyze_code(sample_code, "test.py")
        report = client.generate_report(analysis, format="json")

        # Should be valid JSON
        data = json.loads(report)
        assert "file_path" in data
        assert "summary" in data
        assert "issues" in data

    def test_generate_markdown_report(self, client, sample_code) -> None:
        """Test Markdown report generation."""
        analysis = client.analyze_code(sample_code, "test.py")
        report = client.generate_report(analysis, format="markdown")

        assert isinstance(report, str)
        assert "# Analysis Report" in report
        assert "test.py" in report

    def test_invalid_report_format(self, client, sample_code) -> None:
        """Test error on invalid format."""
        analysis = client.analyze_code(sample_code, "test.py")

        with pytest.raises(ValueError):
            client.generate_report(analysis, format="invalid")

    def test_get_recommendations(self, client) -> None:
        """Test recommendation generation."""
        code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                if x > 1000:
                    if x > 10000:
                        return x
    return 0
"""
        analysis = client.analyze_code(code, "test.py")
        recommendations = client.get_recommendations(analysis)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_recommendations_for_clean_code(self, client, sample_code) -> None:
        """Test recommendations for clean code."""
        analysis = client.analyze_code(sample_code, "test.py")
        recommendations = client.get_recommendations(analysis)

        # Should have recommendations even for good code
        assert isinstance(recommendations, list)

    def test_analyze_file(self, client, tmp_path) -> None:
        """Test file analysis."""
        # Create temp file
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    return 42\n")

        # Analyze
        analysis = client.analyze_file(str(test_file))

        assert analysis is not None
        assert str(test_file) in analysis.file_path

    def test_analyze_nonexistent_file(self, client) -> None:
        """Test error on nonexistent file."""
        with pytest.raises(FileNotFoundError):
            client.analyze_file("/nonexistent/file.py")

    def test_custom_config(self, client, sample_code) -> None:
        """Test with custom configuration."""
        config = AnalyzerConfig(max_complexity=5, max_line_length=80)
        custom_client = AnalyzerClient(config)

        analysis = custom_client.analyze_code(sample_code, "test.py")
        assert analysis is not None

    def test_analysis_summary_methods(self, client) -> None:
        """Test analysis summary methods."""
        code = """
def func1():
    pass

def func2():
    pass

class MyClass:
    pass
"""
        analysis = client.analyze_code(code, "test.py")

        assert analysis.total_issues >= 0
        assert analysis.critical_issues >= 0
        assert analysis.high_issues >= 0

    def test_json_report_structure(self, client, sample_code) -> None:
        """Test JSON report has correct structure."""
        analysis = client.analyze_code(sample_code, "test.py")
        report_json = client.generate_report(analysis, format="json")
        data = json.loads(report_json)

        # Check required fields
        assert "file_path" in data
        assert "file_size" in data
        assert "language" in data
        assert "timestamp" in data
        assert "summary" in data
        assert "issues" in data
        assert "metrics" in data
        assert "patterns" in data

    def test_markdown_report_structure(self, client, sample_code) -> None:
        """Test Markdown report structure."""
        analysis = client.analyze_code(sample_code, "test.py")
        report = client.generate_report(analysis, format="markdown")

        # Check for markdown elements
        assert "# Analysis Report" in report
        assert "## Summary" in report
        assert "- **File size**" in report or "File size" in report


class TestAsyncAnalyzerClient:
    """Test AsyncAnalyzerClient."""

    @pytest.fixture
    def async_client(self) -> AsyncAnalyzerClient:
        """Provide async analyzer client."""
        return AsyncAnalyzerClient()

    @pytest.fixture
    def sample_code(self) -> str:
        """Sample Python code."""
        return 'def foo():\n    """Function."""\n    return 42\n'

    @pytest.mark.asyncio
    async def test_async_analyze_code(self, async_client, sample_code) -> None:
        """Test async code analysis."""
        analysis = await async_client.analyze_code_async(sample_code, "test.py")

        assert analysis is not None
        assert analysis.file_path == "test.py"

    @pytest.mark.asyncio
    async def test_async_analyze_file(self, async_client, tmp_path) -> None:
        """Test async file analysis."""
        # Create temp file
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    pass\n")

        # Analyze
        analysis = await async_client.analyze_file_async(str(test_file))

        assert analysis is not None
        assert str(test_file) in analysis.file_path

    @pytest.mark.asyncio
    async def test_async_analyze_files(self, async_client, tmp_path) -> None:
        """Test async batch file analysis."""
        # Create temp files
        file1 = tmp_path / "test1.py"
        file1.write_text("def foo():\n    pass\n")

        file2 = tmp_path / "test2.py"
        file2.write_text("def bar():\n    pass\n")

        # Analyze
        analyses = await async_client.analyze_files_async(
            [str(file1), str(file2)]
        )

        assert len(analyses) == 2
        assert all(isinstance(a, Analysis) for a in analyses)

    @pytest.mark.asyncio
    async def test_async_batch_code_analysis(self, async_client) -> None:
        """Test async batch code analysis."""
        code_samples = [
            ("def foo():\n    pass", "test1.py"),
            ("def bar():\n    pass", "test2.py"),
        ]

        analyses = await async_client.batch_analyze_code_async(code_samples)

        assert len(analyses) == 2
        assert analyses[0].file_path == "test1.py"
        assert analyses[1].file_path == "test2.py"

    @pytest.mark.asyncio
    async def test_async_generate_report(
        self, async_client, sample_code
    ) -> None:
        """Test async report generation."""
        analysis = await async_client.analyze_code_async(sample_code, "test.py")
        report = await async_client.generate_report_async(analysis, format="text")

        assert isinstance(report, str)
        assert len(report) > 0

    @pytest.mark.asyncio
    async def test_async_get_recommendations(self, async_client) -> None:
        """Test async recommendation generation."""
        code = "def foo():\n    pass\n"
        analysis = await async_client.analyze_code_async(code, "test.py")
        recommendations = await async_client.get_recommendations_async(analysis)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0


class TestClientIntegration:
    """Integration tests for client."""

    def test_full_analysis_workflow(self) -> None:
        """Test complete analysis workflow."""
        client = AnalyzerClient()

        code = '''
"""Test module."""

def calculate(x, y):
    """Add two numbers."""
    if x > 0:
        if y > 0:
            result = x + y
            return result
    return 0
'''

        # Analyze code
        analysis = client.analyze_code(code, "calculator.py")

        # Check results
        assert analysis is not None
        assert analysis.file_path == "calculator.py"
        assert len(analysis.metrics) > 0

        # Generate reports
        text_report = client.generate_report(analysis, format="text")
        json_report = client.generate_report(analysis, format="json")
        md_report = client.generate_report(analysis, format="markdown")

        assert len(text_report) > 0
        assert len(json_report) > 0
        assert len(md_report) > 0

        # Get recommendations
        recommendations = client.get_recommendations(analysis)
        assert isinstance(recommendations, list)

    def test_syntax_error_handling(self) -> None:
        """Test handling of syntax errors."""
        client = AnalyzerClient()

        code = "def broken(\n  invalid syntax"
        analysis = client.analyze_code(code, "broken.py")

        # Should detect syntax error
        assert len(analysis.issues) > 0
        assert any(i.issue_type == "syntax" for i in analysis.issues)

    def test_empty_code_analysis(self) -> None:
        """Test analysis of empty code."""
        client = AnalyzerClient()

        analysis = client.analyze_code("", "empty.py")

        assert analysis is not None
        assert analysis.file_size == 0
