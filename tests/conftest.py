"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from socratic_analyzer import AnalyzerConfig


@pytest.fixture
def sample_python_code() -> str:
    """Provide sample Python code for testing."""
    return '''
def calculate_fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


class DataProcessor:
    """Process data from various sources."""

    def __init__(self):
        self.data = []
        self.processed = False

    def process(self, items):
        for item in items:
            if item not in self.data:
                self.data.append(item)
        self.processed = True

    def get_results(self):
        return self.data
'''


@pytest.fixture
def sample_file(tmp_path) -> Path:
    """Create a temporary Python file with sample code."""
    file_path = tmp_path / "sample.py"
    file_path.write_text(
        '''
def badly_named_func(x, y, z):
    """Missing docstring details."""
    a = 1
    b = 2
    c = x + y + z
    d = a + b + c
    e = d * 2
    f = e + 1
    g = f * x
    return g
'''
    )
    return file_path


@pytest.fixture
def temp_project_dir(tmp_path) -> Path:
    """Create a temporary project directory with multiple Python files."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create multiple Python files
    (project_dir / "module1.py").write_text(
        '''
def function_one(x):
    """Function one."""
    return x * 2

def function_two(y):
    return y + 1
'''
    )

    (project_dir / "module2.py").write_text(
        '''
class MyClass:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def get_value(self):
        return self.value
'''
    )

    return project_dir


@pytest.fixture
def analyzer_config() -> AnalyzerConfig:
    """Provide default analyzer configuration."""
    return AnalyzerConfig(
        analyze_types=True,
        analyze_docstrings=True,
        analyze_security=True,
        analyze_performance=True,
        max_complexity=10,
        max_line_length=120,
    )
