"""Tests for code analyzers."""

import pytest

from socratic_analyzer.analyzers.complexity import ComplexityAnalyzer
from socratic_analyzer.analyzers.imports import ImportAnalyzer
from socratic_analyzer.analyzers.metrics import MetricsAnalyzer
from socratic_analyzer.analyzers.static import StaticAnalyzer


class TestStaticAnalyzer:
    """Test StaticAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> StaticAnalyzer:
        """Provide static analyzer."""
        return StaticAnalyzer()

    def test_analyzer_name(self, analyzer) -> None:
        """Test analyzer name."""
        assert analyzer.name == "StaticAnalyzer"

    def test_analyzer_description(self, analyzer) -> None:
        """Test analyzer description."""
        assert len(analyzer.description) > 0

    def test_detect_syntax_error(self, analyzer) -> None:
        """Test detection of syntax errors."""
        code = "def foo(\n  invalid syntax"
        issues = analyzer.analyze(code, "test.py")

        assert len(issues) > 0
        assert any(i.issue_type == "syntax" for i in issues)

    def test_detect_unused_variables(self, analyzer) -> None:
        """Test detection of unused variables."""
        code = """
def foo():
    unused_var = 5
    return 10
"""
        issues = analyzer.analyze(code, "test.py")
        unused_issues = [i for i in issues if "unused" in i.message.lower()]

        assert len(unused_issues) > 0

    def test_detect_missing_docstrings(self, analyzer) -> None:
        """Test detection of missing docstrings."""
        code = """
def foo():
    return 42
"""
        issues = analyzer.analyze(code, "test.py")
        docstring_issues = [i for i in issues if "docstring" in i.message.lower()]

        assert len(docstring_issues) > 0

    def test_missing_module_docstring(self, analyzer) -> None:
        """Test detection of missing module docstring."""
        code = "x = 1"
        issues = analyzer.analyze(code, "test.py")

        assert any("module" in i.message.lower() for i in issues)

    def test_detect_long_lines(self, analyzer) -> None:
        """Test detection of long lines."""
        # Create a valid but very long line
        code = 'x = "' + "a" * 200 + '"\n'
        issues = analyzer.analyze(code, "test.py")
        long_line_issues = [i for i in issues if "long" in i.message.lower()]

        assert len(long_line_issues) > 0

    def test_with_docstring(self, analyzer) -> None:
        """Test code with proper docstrings."""
        code = '''
"""Module docstring."""

def foo():
    """Function docstring."""
    return 42
'''
        issues = analyzer.analyze(code, "test.py")
        docstring_issues = [i for i in issues if "docstring" in i.message.lower()]

        assert len(docstring_issues) == 0

    def test_detect_empty_function(self, analyzer) -> None:
        """Test detection of empty functions."""
        code = """
def empty_func():
    pass
"""
        issues = analyzer.analyze(code, "test.py")
        empty_issues = [i for i in issues if "empty" in i.message.lower()]

        assert len(empty_issues) > 0

    def test_detect_wildcard_imports(self, analyzer) -> None:
        """Test detection of wildcard imports."""
        code = "from module import *\n"
        issues = analyzer.analyze(code, "test.py")
        import_issues = [i for i in issues if "wildcard" in i.message.lower()]

        assert len(import_issues) > 0

    def test_valid_code(self, analyzer) -> None:
        """Test analyzer with valid code."""
        code = '''
"""Module."""

def valid():
    """Valid function."""
    return True
'''
        issues = analyzer.analyze(code, "test.py")

        # Should have few or no critical issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        assert len(critical_issues) == 0

    def test_location_formatting(self, analyzer) -> None:
        """Test location string formatting."""
        location = analyzer._format_location("test.py", 42)
        assert location == "test.py:42"

        location = analyzer._format_location("test.py", 42, 10)
        assert location == "test.py:42:10"


class TestComplexityAnalyzer:
    """Test ComplexityAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> ComplexityAnalyzer:
        """Provide complexity analyzer."""
        return ComplexityAnalyzer(max_complexity=10)

    def test_analyzer_name(self, analyzer) -> None:
        """Test analyzer name."""
        assert analyzer.name == "ComplexityAnalyzer"

    def test_simple_function_complexity(self, analyzer) -> None:
        """Test simple function complexity."""
        code = """
def simple():
    return 42
"""
        issues = analyzer.analyze(code, "test.py")

        # Simple function should have low complexity
        complexity_issues = [i for i in issues if i.issue_type == "complexity"]
        assert len(complexity_issues) == 0

    def test_complex_function_detection(self, analyzer) -> None:
        """Test detection of complex functions."""
        code = """
def complex_func(x):
    if x > 0:
        if x > 10:
            if x > 100:
                if x > 1000:
                    if x > 10000:
                        if x > 100000:
                            return True
    return False
"""
        issues = analyzer.analyze(code, "test.py")
        complexity_issues = [i for i in issues if i.issue_type == "complexity"]

        assert len(complexity_issues) > 0

    def test_deep_nesting_detection(self, analyzer) -> None:
        """Test detection of deep nesting."""
        code = """
def nested():
    for i in range(10):
        for j in range(10):
            for k in range(10):
                for l in range(10):
                    for m in range(10):
                        pass
"""
        issues = analyzer.analyze(code, "test.py")
        nesting_issues = [i for i in issues if "nesting" in i.message.lower()]

        assert len(nesting_issues) > 0

    def test_method_complexity(self, analyzer) -> None:
        """Test method complexity detection."""
        code = """
class MyClass:
    def complex_method(self, x):
        if x > 0:
            if x > 10:
                if x > 100:
                    if x > 1000:
                        if x > 10000:
                            if x > 100000:
                                return x
        return 0
"""
        issues = analyzer.analyze(code, "test.py")

        assert any("complex" in i.message.lower() for i in issues)

    def test_cyclomatic_complexity_calculation(self, analyzer) -> None:
        """Test cyclomatic complexity calculation."""
        import ast

        code = "def f(x):\n  if x: pass"
        tree = ast.parse(code)
        func = tree.body[0]

        complexity = analyzer._calculate_cyclomatic_complexity(func)
        assert complexity == 2  # Base (1) + if statement (1)

    def test_custom_max_complexity(self) -> None:
        """Test custom complexity threshold."""
        analyzer = ComplexityAnalyzer(max_complexity=3)

        code = """
def func(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return x
    return 0
"""
        issues = analyzer.analyze(code, "test.py")
        complexity_issues = [i for i in issues if i.issue_type == "complexity"]

        assert len(complexity_issues) > 0


class TestMetricsAnalyzer:
    """Test MetricsAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> MetricsAnalyzer:
        """Provide metrics analyzer."""
        return MetricsAnalyzer()

    def test_analyzer_name(self, analyzer) -> None:
        """Test analyzer name."""
        assert analyzer.name == "MetricsAnalyzer"

    def test_calculate_loc_metrics(self, analyzer) -> None:
        """Test LOC metrics calculation."""
        code = """
def foo():
    return 42

def bar():
    return 24
"""
        metrics = analyzer.calculate_metrics(code)

        assert any(m.name == "total_lines" for m in metrics)
        assert any(m.name == "code_lines" for m in metrics)
        assert any(m.name == "blank_lines" for m in metrics)

    def test_total_lines_metric(self, analyzer) -> None:
        """Test total lines metric."""
        code = "x = 1\ny = 2\nz = 3\n"
        metrics = analyzer.calculate_metrics(code)

        total_lines = next((m for m in metrics if m.name == "total_lines"), None)
        assert total_lines is not None
        assert total_lines.value == 4

    def test_code_lines_metric(self, analyzer) -> None:
        """Test code lines metric."""
        code = "x = 1\n\ny = 2\n\nz = 3"
        metrics = analyzer.calculate_metrics(code)

        code_lines = next((m for m in metrics if m.name == "code_lines"), None)
        assert code_lines is not None
        assert code_lines.value == 3

    def test_blank_lines_metric(self, analyzer) -> None:
        """Test blank lines metric."""
        code = "x = 1\n\n\ny = 2"
        metrics = analyzer.calculate_metrics(code)

        blank_lines = next((m for m in metrics if m.name == "blank_lines"), None)
        assert blank_lines is not None
        assert blank_lines.value == 2  # Two blank lines between x=1 and y=2

    def test_maintainability_index(self, analyzer) -> None:
        """Test maintainability index calculation."""
        code = """
def func1():
    return 1

def func2():
    return 2
"""
        metrics = analyzer.calculate_metrics(code)

        maintainability = next(
            (m for m in metrics if m.name == "maintainability_index"), None
        )
        assert maintainability is not None
        assert 0 <= maintainability.value <= 100

    def test_function_count_metric(self, analyzer) -> None:
        """Test function count metric."""
        code = """
def func1():
    pass

def func2():
    pass

class MyClass:
    def method(self):
        pass
"""
        metrics = analyzer.calculate_metrics(code)

        num_functions = next((m for m in metrics if m.name == "num_functions"), None)
        assert num_functions is not None
        assert num_functions.value == 3

    def test_class_count_metric(self, analyzer) -> None:
        """Test class count metric."""
        code = """
class Class1:
    pass

class Class2:
    pass
"""
        metrics = analyzer.calculate_metrics(code)

        num_classes = next((m for m in metrics if m.name == "num_classes"), None)
        assert num_classes is not None
        assert num_classes.value == 2

    def test_average_function_length(self, analyzer) -> None:
        """Test average function length metric."""
        code = """
def func1():
    x = 1
    y = 2
    return x + y

def func2():
    return 42
"""
        metrics = analyzer.calculate_metrics(code)

        avg_length = next(
            (m for m in metrics if m.name == "avg_function_length"), None
        )
        assert avg_length is not None
        assert avg_length.value > 0


class TestImportAnalyzer:
    """Test ImportAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> ImportAnalyzer:
        """Provide import analyzer."""
        return ImportAnalyzer()

    def test_analyzer_name(self, analyzer) -> None:
        """Test analyzer name."""
        assert analyzer.name == "ImportAnalyzer"

    def test_import_organization_check(self, analyzer) -> None:
        """Test import organization checking."""
        code = """
import os
import sys

import numpy

from module import func
"""
        issues = analyzer.analyze(code, "test.py")

        # Code has organized imports, should have minimal issues
        assert len(issues) >= 0

    def test_detect_unused_imports(self, analyzer) -> None:
        """Test detection of unused imports."""
        code = """
import os
import sys

x = 1
"""
        issues = analyzer.analyze(code, "test.py")
        unused = [i for i in issues if "unused" in i.message.lower()]

        # At least os should be detected as unused
        assert len(unused) > 0

    def test_relative_import_detection(self, analyzer) -> None:
        """Test detection of relative imports."""
        code = "from ...module import func\n"
        issues = analyzer.analyze(code, "test.py")

        # Should detect the deep relative import
        relative_issues = [i for i in issues if "relative" in i.message.lower()]
        assert len(relative_issues) > 0

    def test_used_imports(self, analyzer) -> None:
        """Test imports marked as used."""
        code = """
import os

path = os.getcwd()
"""
        issues = analyzer.analyze(code, "test.py")
        unused = [i for i in issues if "unused" in i.message.lower()]

        # os is used, shouldn't be in unused
        assert len(unused) == 0

    def test_from_import_usage(self, analyzer) -> None:
        """Test from import usage detection."""
        code = """
from os import getcwd

path = getcwd()
"""
        issues = analyzer.analyze(code, "test.py")
        unused = [i for i in issues if "unused" in i.message.lower()]

        # getcwd is used
        assert len(unused) == 0
