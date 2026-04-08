"""Test execution framework for Socratic Analyzer."""

import ast
import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TestResult:
    """Result of a single test execution."""

    test_name: str
    file_path: str
    status: str  # "passed", "failed", "error", "skipped"
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    assertion_details: Optional[str] = None

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.test_name}: {self.status}"


@dataclass
class TestSuiteResult:
    """Results for a test suite/module."""

    file_path: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration_ms: float = 0.0
    tests: List[TestResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return ((self.total_tests - self.failed - self.errors) / self.total_tests) * 100

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"TestSuite({self.file_path}, "
            f"passed={self.passed}/{self.total_tests}, "
            f"success={self.success_rate:.1f}%)"
        )


@dataclass
class CoverageReport:
    """Code coverage analysis."""

    total_lines: int = 0
    covered_lines: int = 0
    coverage_percentage: float = 0.0
    uncovered_files: List[str] = field(default_factory=list)
    missing_line_numbers: Dict[str, List[int]] = field(default_factory=dict)

    @property
    def coverage_status(self) -> str:
        """Get coverage status."""
        if self.coverage_percentage >= 90:
            return "excellent"
        elif self.coverage_percentage >= 70:
            return "good"
        elif self.coverage_percentage >= 50:
            return "fair"
        else:
            return "poor"


class TestDiscoverer:
    """Discovers test files and test functions in a project."""

    # Common test file patterns
    TEST_FILE_PATTERNS = [
        "test_*.py",
        "*_test.py",
        "tests.py",
    ]

    # Common test function/class patterns
    TEST_FUNCTION_PATTERN = re.compile(r"^def\s+test_\w+")
    TEST_CLASS_PATTERN = re.compile(r"^class\s+Test\w+")

    @staticmethod
    def discover_test_files(project_path: str) -> List[str]:
        """
        Discover all test files in a project.

        Args:
            project_path: Root path of the project

        Returns:
            List of test file paths
        """
        project_root = Path(project_path)
        test_files = []

        for pattern in TestDiscoverer.TEST_FILE_PATTERNS:
            test_files.extend(project_root.rglob(pattern))

        # Filter out venv, env, site-packages, etc.
        filtered_files = [
            str(f)
            for f in test_files
            if not any(
                part in str(f).split("/")
                for part in ["venv", "env", ".venv", "site-packages", "__pycache__"]
            )
        ]

        return sorted(set(filtered_files))

    @staticmethod
    def discover_tests_in_file(file_path: str) -> List[str]:
        """
        Discover test functions/classes in a file.

        Args:
            file_path: Path to test file

        Returns:
            List of test names (function and class names)
        """
        tests = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("test_"):
                        tests.append(f"{Path(file_path).stem}::{node.name}")

                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith("Test"):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                                tests.append(f"{Path(file_path).stem}::{node.name}::{item.name}")

        except (SyntaxError, OSError) as e:
            logging.warning(f"Failed to parse {file_path}: {e}")

        return tests


class TestExecutor:
    """Executes tests using pytest or unittest."""

    def __init__(self, project_path: str, timeout_seconds: int = 60):
        """
        Initialize test executor.

        Args:
            project_path: Root path of the project
            timeout_seconds: Timeout for test execution
        """
        self.project_path = Path(project_path)
        self.timeout_seconds = timeout_seconds
        self.logger = logging.getLogger(__name__)

    def execute_tests(self, test_files: Optional[List[str]] = None) -> List[TestSuiteResult]:
        """
        Execute tests and collect results.

        Args:
            test_files: Specific test files to run. If None, discovers all test files.

        Returns:
            List of TestSuiteResult for each test file
        """
        if test_files is None:
            test_files = TestDiscoverer.discover_test_files(str(self.project_path))

        if not test_files:
            self.logger.warning("No test files found")
            return []

        # Try pytest first, fall back to unittest
        if self._has_pytest():
            return self._execute_with_pytest(test_files)
        else:
            return self._execute_with_unittest(test_files)

    def _has_pytest(self) -> bool:
        """Check if pytest is installed."""
        try:
            subprocess.run(
                ["pytest", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _execute_with_pytest(self, test_files: List[str]) -> List[TestSuiteResult]:
        """
        Execute tests using pytest.

        Args:
            test_files: List of test file paths

        Returns:
            List of TestSuiteResult
        """
        results = []

        for test_file in test_files:
            try:
                # Run pytest with JSON output
                result = subprocess.run(
                    [
                        "pytest",
                        test_file,
                        "-v",
                        "--tb=short",
                        "--quiet",
                        "-q",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    cwd=str(self.project_path),
                )

                suite_result = self._parse_pytest_output(test_file, result)
                results.append(suite_result)

            except subprocess.TimeoutExpired:
                self.logger.error(f"Test execution timeout for {test_file}")
                suite_result = TestSuiteResult(
                    file_path=test_file,
                    errors=1,
                    error_message="Test execution timeout",
                )
                results.append(suite_result)
            except Exception as e:
                self.logger.error(f"Failed to execute tests in {test_file}: {e}")
                suite_result = TestSuiteResult(
                    file_path=test_file,
                    errors=1,
                    error_message=str(e),
                )
                results.append(suite_result)

        return results

    def _execute_with_unittest(self, test_files: List[str]) -> List[TestSuiteResult]:
        """
        Execute tests using unittest.

        Args:
            test_files: List of test file paths

        Returns:
            List of TestSuiteResult
        """
        results = []

        for test_file in test_files:
            try:
                # Convert file path to module name
                module_path = Path(test_file).relative_to(self.project_path)
                module_name = str(module_path).replace("/", ".").replace("\\", ".")[:-3]

                result = subprocess.run(
                    [
                        "python",
                        "-m",
                        "unittest",
                        module_name,
                        "-v",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    cwd=str(self.project_path),
                )

                suite_result = self._parse_unittest_output(test_file, result)
                results.append(suite_result)

            except subprocess.TimeoutExpired:
                self.logger.error(f"Test execution timeout for {test_file}")
                suite_result = TestSuiteResult(
                    file_path=test_file,
                    errors=1,
                    error_message="Test execution timeout",
                )
                results.append(suite_result)
            except Exception as e:
                self.logger.error(f"Failed to execute tests in {test_file}: {e}")
                suite_result = TestSuiteResult(
                    file_path=test_file,
                    errors=1,
                    error_message=str(e),
                )
                results.append(suite_result)

        return results

    def _parse_pytest_output(
        self, test_file: str, result: subprocess.CompletedProcess
    ) -> TestSuiteResult:
        """
        Parse pytest output and create TestSuiteResult.

        Args:
            test_file: Test file path
            result: Completed subprocess result

        Returns:
            TestSuiteResult with parsed data
        """
        suite_result = TestSuiteResult(file_path=test_file)

        # Parse output for test counts
        output = result.stdout + result.stderr

        # Extract pass/fail counts from pytest output
        import re

        match = re.search(r"(\d+) passed", output)
        suite_result.passed = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) failed", output)
        suite_result.failed = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) error", output)
        suite_result.errors = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) skipped", output)
        suite_result.skipped = int(match.group(1)) if match else 0

        suite_result.total_tests = suite_result.passed + suite_result.failed + suite_result.errors

        if result.returncode != 0:
            suite_result.error_message = "Some tests failed"

        return suite_result

    def _parse_unittest_output(
        self, test_file: str, result: subprocess.CompletedProcess
    ) -> TestSuiteResult:
        """
        Parse unittest output and create TestSuiteResult.

        Args:
            test_file: Test file path
            result: Completed subprocess result

        Returns:
            TestSuiteResult with parsed data
        """
        suite_result = TestSuiteResult(file_path=test_file)

        output = result.stdout + result.stderr

        # Parse unittest format: "... ok" or "F" or "E"
        import re

        # Count test runs and failures
        test_count_match = re.search(r"Ran (\d+) test", output)
        if test_count_match:
            suite_result.total_tests = int(test_count_match.group(1))

        # Check for failures
        failures_match = re.search(r"failures=(\d+)", output)
        if failures_match:
            suite_result.failed = int(failures_match.group(1))

        errors_match = re.search(r"errors=(\d+)", output)
        if errors_match:
            suite_result.errors = int(errors_match.group(1))

        suite_result.passed = suite_result.total_tests - suite_result.failed - suite_result.errors

        if result.returncode != 0:
            suite_result.error_message = "Some tests failed"

        return suite_result

    def get_coverage(self) -> Optional[CoverageReport]:
        """
        Get code coverage report using coverage.py.

        Returns:
            CoverageReport or None if coverage not available
        """
        try:
            # Run coverage
            subprocess.run(
                ["coverage", "run", "-m", "pytest"],
                capture_output=True,
                timeout=self.timeout_seconds,
                cwd=str(self.project_path),
            )

            # Get coverage report as JSON
            coverage_result = subprocess.run(
                ["coverage", "json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_path),
            )

            if coverage_result.returncode == 0:
                json_file = self.project_path / "coverage.json"

                if json_file.exists():
                    with open(json_file) as f:
                        coverage_data = json.load(f)

                    report = CoverageReport()
                    if "totals" in coverage_data:
                        report.coverage_percentage = coverage_data["totals"].get(
                            "percent_covered", 0
                        )
                        report.total_lines = coverage_data["totals"].get("num_statements", 0)
                        report.covered_lines = int(
                            report.coverage_percentage / 100 * report.total_lines
                        )

                    return report

        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
            self.logger.warning("Failed to generate coverage report")

        return None


class TestAnalyzer:
    """Analyzes test coverage and identifies missing tests."""

    @staticmethod
    def analyze_coverage_gaps(
        project_path: str, source_files: List[str], test_results: List[TestSuiteResult]
    ) -> Dict[str, List[str]]:
        """
        Analyze coverage gaps and identify untested modules.

        Args:
            project_path: Root path of the project
            source_files: List of source file paths
            test_results: List of test execution results

        Returns:
            Dictionary mapping file paths to list of untested functions/classes
        """
        gaps = {}
        test_count = sum(r.total_tests for r in test_results)

        if test_count == 0:
            gaps["_summary"] = ["No tests found in project"]
            return gaps

        for source_file in source_files:
            untested = TestAnalyzer._find_untested_items(source_file, project_path)
            if untested:
                gaps[source_file] = untested

        return gaps

    @staticmethod
    def _find_untested_items(file_path: str, project_path: str) -> List[str]:
        """
        Find functions and classes that should have tests.

        Args:
            file_path: Path to source file
            project_path: Project root path

        Returns:
            List of untested function/class names
        """
        untested = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions and dunder methods
                    if not node.name.startswith("_"):
                        # Would need actual test file mapping to determine if tested
                        # For now, just identify public functions
                        untested.append(f"def {node.name}")

                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):
                        untested.append(f"class {node.name}")

        except (SyntaxError, OSError):
            pass

        return untested[:10]  # Limit to top 10 suggestions
