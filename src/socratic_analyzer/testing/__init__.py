"""Test execution framework for Socratic Analyzer."""

from .executor import (
    TestResult,
    TestSuiteResult,
    CoverageReport,
    TestDiscoverer,
    TestExecutor,
    TestAnalyzer,
)

__all__ = [
    "TestResult",
    "TestSuiteResult",
    "CoverageReport",
    "TestDiscoverer",
    "TestExecutor",
    "TestAnalyzer",
]
