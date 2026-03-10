"""Tests for Openclaw integration."""

import pytest

from socratic_analyzer.integrations.openclaw import SocraticAnalyzerSkill


class TestSocraticAnalyzerSkill:
    """Test SocraticAnalyzerSkill."""

    @pytest.fixture
    def skill(self) -> SocraticAnalyzerSkill:
        """Provide analyzer skill."""
        return SocraticAnalyzerSkill()

    @pytest.fixture
    def sample_code(self) -> str:
        """Sample Python code."""
        return '''
def calculate(x, y):
    """Calculate sum."""
    return x + y

class Calculator:
    """Simple calculator."""

    def add(self, a, b):
        return a + b
'''

    @pytest.fixture
    def problematic_code(self) -> str:
        """Code with issues."""
        return '''
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                if x > 1000:
                    if x > 10000:
                        return x
    return 0

global_var = 10

def bad_except():
    try:
        risky()
    except:
        pass
'''

    def test_skill_initialization(self, skill) -> None:
        """Test skill initialization."""
        assert skill.client is not None

    def test_analyze_code(self, skill, sample_code) -> None:
        """Test code analysis."""
        result = skill.analyze_code(sample_code)

        assert "quality_score" in result
        assert "total_issues" in result
        assert "file_path" in result
        assert isinstance(result["quality_score"], (int, float))

    def test_analyze_file(self, skill, tmp_path) -> None:
        """Test file analysis."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    return 42\n")

        result = skill.analyze_file(str(test_file))

        assert result["file_path"] == str(test_file)
        assert "quality_score" in result

    def test_analyze_files(self, skill, tmp_path) -> None:
        """Test batch file analysis."""
        file1 = tmp_path / "test1.py"
        file1.write_text("def foo():\n    return 1\n")

        file2 = tmp_path / "test2.py"
        file2.write_text("def bar():\n    return 2\n")

        result = skill.analyze_files([str(file1), str(file2)])

        assert result["files_analyzed"] == 2
        assert result["files_successful"] == 2
        assert "average_quality_score" in result

    def test_get_quality_score(self, skill, sample_code) -> None:
        """Test quality score calculation."""
        score = skill.get_quality_score(sample_code)

        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_get_quality_report(self, skill, sample_code) -> None:
        """Test quality report generation."""
        report = skill.get_quality_report(sample_code)

        assert "overall_score" in report
        assert "rating" in report
        assert "issue_count" in report
        assert "suggestions" in report

    def test_get_recommendations(self, skill, problematic_code) -> None:
        """Test recommendations generation."""
        recommendations = skill.get_recommendations(problematic_code)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_detect_patterns(self, skill) -> None:
        """Test pattern detection."""
        code = '''
class Singleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
'''
        patterns = skill.detect_patterns(code)

        assert isinstance(patterns, list)

    def test_detect_issues(self, skill, problematic_code) -> None:
        """Test issue detection."""
        issues = skill.detect_issues(problematic_code)

        assert isinstance(issues, list)
        assert len(issues) > 0
        assert all("type" in i for i in issues)
        assert all("severity" in i for i in issues)

    def test_detect_issues_by_severity(self, skill, problematic_code) -> None:
        """Test filtering issues by severity."""
        critical_issues = skill.detect_issues(problematic_code, severity="high")

        assert isinstance(critical_issues, list)
        # All returned issues should have the specified severity
        for issue in critical_issues:
            assert issue["severity"] == "high"

    def test_generate_report_text(self, skill, sample_code) -> None:
        """Test text report generation."""
        report = skill.generate_report(sample_code, format="text")

        assert isinstance(report, str)
        assert len(report) > 0
        assert "Analysis Report" in report

    def test_generate_report_json(self, skill, sample_code) -> None:
        """Test JSON report generation."""
        report = skill.generate_report(sample_code, format="json")

        assert isinstance(report, str)
        assert len(report) > 0
        # Should be valid JSON
        import json
        data = json.loads(report)
        assert "file_path" in data

    def test_generate_report_markdown(self, skill, sample_code) -> None:
        """Test Markdown report generation."""
        report = skill.generate_report(sample_code, format="markdown")

        assert isinstance(report, str)
        assert len(report) > 0
        assert "# Analysis Report" in report

    def test_check_quality_threshold_pass(self, skill, sample_code) -> None:
        """Test threshold check with passing score."""
        result = skill.check_quality_threshold(sample_code, threshold=50.0)

        assert "passes_threshold" in result
        assert "score" in result
        assert "threshold" in result

    def test_check_quality_threshold_fail(self, skill, problematic_code) -> None:
        """Test threshold check with failing score."""
        result = skill.check_quality_threshold(problematic_code, threshold=90.0)

        assert result["threshold"] == 90.0
        assert "gap" in result

    def test_compare_codes(self, skill) -> None:
        """Test comparing two code samples."""
        code1 = "x = 1\ny = 2\n"
        code2 = "x = 1\ny = 2\nz = 3\n"

        result = skill.compare_codes(code1, code2)

        assert "code1_score" in result
        assert "code2_score" in result
        assert "winner" in result
        assert result["winner"] in ("code1", "code2", "tie")

    def test_skill_with_custom_config(self) -> None:
        """Test skill with custom configuration."""
        skill = SocraticAnalyzerSkill(max_complexity=5, include_metrics=False)

        code = "if x: pass\n"
        analysis = skill.client.analyze_code(code)

        # Should respect custom config
        assert skill.client.config.max_complexity == 5
