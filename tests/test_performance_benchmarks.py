"""Performance benchmarks for Socratic Analyzer."""

import pytest
from socratic_analyzer.client import AnalyzerClient


class TestAnalyzerPerformance:
    """Performance benchmarks for analyzer components."""

    @pytest.fixture
    def client(self) -> AnalyzerClient:
        """Provide analyzer client."""
        return AnalyzerClient()

    @pytest.fixture
    def small_code(self) -> str:
        """Small code sample (simple function)."""
        return '''
def add(x, y):
    """Add two numbers."""
    return x + y
'''

    @pytest.fixture
    def medium_code(self) -> str:
        """Medium code sample (multiple classes/functions)."""
        return '''
class Calculator:
    """Simple calculator."""

    def add(self, a, b):
        """Add numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract numbers."""
        return a - b

    def multiply(self, a, b):
        """Multiply numbers."""
        return a * b

    def divide(self, a, b):
        """Divide numbers."""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

def process_items(items):
    """Process list of items."""
    results = []
    for item in items:
        if item > 0:
            results.append(item * 2)
    return results

class DataProcessor:
    """Process data efficiently."""

    def __init__(self, data):
        """Initialize with data."""
        self.data = data

    def filter_data(self, threshold):
        """Filter data above threshold."""
        return [item for item in self.data if item > threshold]

    def transform(self, func):
        """Transform data with function."""
        return [func(item) for item in self.data]
'''

    @pytest.fixture
    def large_code(self) -> str:
        """Large code sample (complex project)."""
        code = '''
class BaseAnalyzer:
    """Base analyzer class."""

    def analyze(self, code):
        """Analyze code."""
        pass
'''
        # Add many functions and classes
        for i in range(20):
            code += f'''
def function_{i}(x, y, z):
    """Function {i}."""
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
    return 0

class Class_{i}:
    """Class {i}."""

    def method_1(self):
        return 1

    def method_2(self):
        return 2

    def method_3(self):
        return 3
'''
        return code

    def test_small_code_analysis_speed(self, client, small_code) -> None:
        """Test analysis speed for small code (should be < 100ms)."""
        import time

        start = time.time()
        analysis = client.analyze_code(small_code, "small.py")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100, f"Small code analysis took {elapsed}ms (expected < 100ms)"
        assert len(analysis.issues) >= 0

    def test_medium_code_analysis_speed(self, client, medium_code) -> None:
        """Test analysis speed for medium code (should be < 500ms)."""
        import time

        start = time.time()
        analysis = client.analyze_code(medium_code, "medium.py")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 500, f"Medium code analysis took {elapsed}ms (expected < 500ms)"
        assert len(analysis.issues) >= 0

    def test_large_code_analysis_speed(self, client, large_code) -> None:
        """Test analysis speed for large code (should be < 2000ms)."""
        import time

        start = time.time()
        analysis = client.analyze_code(large_code, "large.py")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 2000, f"Large code analysis took {elapsed}ms (expected < 2000ms)"
        assert len(analysis.issues) >= 0

    def test_report_generation_speed(self, client, medium_code) -> None:
        """Test report generation speed (should be < 100ms)."""
        import time

        analysis = client.analyze_code(medium_code, "test.py")

        start = time.time()
        report = client.generate_report(analysis, format="text")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100, f"Report generation took {elapsed}ms (expected < 100ms)"
        assert len(report) > 0

    def test_json_report_generation_speed(self, client, medium_code) -> None:
        """Test JSON report generation speed (should be < 100ms)."""
        import time

        analysis = client.analyze_code(medium_code, "test.py")

        start = time.time()
        report = client.generate_report(analysis, format="json")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100, f"JSON report took {elapsed}ms (expected < 100ms)"
        assert len(report) > 0

    def test_recommendations_speed(self, client, medium_code) -> None:
        """Test recommendation generation speed (should be < 50ms)."""
        import time

        analysis = client.analyze_code(medium_code, "test.py")

        start = time.time()
        recommendations = client.get_recommendations(analysis)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 50, f"Recommendations took {elapsed}ms (expected < 50ms)"
        assert len(recommendations) > 0

    def test_memory_efficiency_large_code(self, client, large_code) -> None:
        """Test memory efficiency with large code."""
        import sys

        analysis = client.analyze_code(large_code, "large.py")

        # Analysis object should be reasonably sized
        size = sys.getsizeof(analysis)
        assert size < 1000000, f"Analysis object too large: {size} bytes (expected < 1MB)"

    def test_analyzer_instantiation_speed(self) -> None:
        """Test client initialization speed (should be < 100ms)."""
        import time

        start = time.time()
        client = AnalyzerClient()
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100, f"Client init took {elapsed}ms (expected < 100ms)"
        assert client is not None

    def test_concurrent_analysis_speed(self, client) -> None:
        """Test speed of analyzing multiple code samples."""
        import time

        codes = [
            f"def func_{i}(x):\n    return x * {i}\n"
            for i in range(5)
        ]

        start = time.time()
        results = [client.analyze_code(code, f"file_{i}.py") for i, code in enumerate(codes)]
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 500, f"Concurrent analysis took {elapsed}ms (expected < 500ms)"
        assert len(results) == 5

    @pytest.mark.benchmark
    def test_analysis_benchmark(self, benchmark, client, medium_code) -> None:
        """Benchmark analysis performance."""
        result = benchmark(client.analyze_code, medium_code, "benchmark.py")
        assert result is not None
