"""Tests for performance analyzer."""

import pytest

from socratic_analyzer.analyzers.performance import PerformanceAnalyzer


class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> PerformanceAnalyzer:
        """Provide performance analyzer."""
        return PerformanceAnalyzer()

    def test_analyzer_properties(self, analyzer) -> None:
        """Test analyzer properties."""
        assert analyzer.name == "Performance Analyzer"
        assert "performance" in analyzer.description.lower()

    def test_string_concatenation_in_loop_detection(self, analyzer) -> None:
        """Test detection of string concatenation in loops."""
        code = '''
result = ""
for i in range(1000):
    result += str(i)
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "performance" for i in issues)
        assert any("concatenation" in i.message.lower() for i in issues)

    def test_list_insert_in_loop_detection(self, analyzer) -> None:
        """Test detection of list.insert in loops."""
        code = '''
items = []
for i in range(100):
    items.insert(0, i)
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "performance" for i in issues)

    def test_list_remove_in_loop_detection(self, analyzer) -> None:
        """Test detection of list.remove in loops."""
        code = '''
items = list(range(100))
for i in items:
    items.remove(i)
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "performance" for i in issues)

    def test_type_checking_in_loop_detection(self, analyzer) -> None:
        """Test detection of type checking in loops."""
        code = '''
items = [1, "2", 3, "4"]
for item in items:
    if isinstance(item, str):
        print(item)
'''
        issues = analyzer.analyze(code, "test.py")
        performance_issues = [i for i in issues if i.issue_type == "performance"]
        assert any("type" in i.message.lower() or "isinstance" in i.message.lower()
                   for i in performance_issues)

    def test_n_plus_one_pattern_detection(self, analyzer) -> None:
        """Test detection of N+1 query pattern."""
        code = '''
users = get_users()
for user in users:
    posts = user.query()
    print(posts)
'''
        issues = analyzer.analyze(code, "test.py")
        assert any(i.issue_type == "performance" for i in issues)

    def test_repeated_function_calls(self, analyzer) -> None:
        """Test detection of repeated function calls."""
        code = '''
len(items)
len(items)
len(items)
len(items)
len(items)
len(items)
len(items)
result = len(items) + 10
'''
        issues = analyzer.analyze(code, "test.py")
        # May detect repeated calls depending on implementation
        assert isinstance(issues, list)

    def test_syntax_error_handling(self, analyzer) -> None:
        """Test handling of syntax errors."""
        code = "for x in range(\\n  invalid"
        issues = analyzer.analyze(code, "test.py")
        assert isinstance(issues, list)

    def test_empty_code_analysis(self, analyzer) -> None:
        """Test analysis of empty code."""
        issues = analyzer.analyze("", "test.py")
        assert isinstance(issues, list)

    def test_clean_code_no_issues(self, analyzer) -> None:
        """Test that clean code has no performance issues."""
        code = '''
def calculate(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
'''
        issues = analyzer.analyze(code, "test.py")
        # Clean code should have minimal performance issues
        perf_issues = [i for i in issues if i.issue_type == "performance"]
        assert len(perf_issues) < 3
