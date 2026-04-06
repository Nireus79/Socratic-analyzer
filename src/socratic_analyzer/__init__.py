"""Socratic Analyzer - Production-grade code analysis package."""

__version__ = "0.1.0"
__author__ = "Socratic Analyzer"
__email__ = "info@socratic-analyzer.dev"

from .async_client import AsyncAnalyzerClient
from .client import AnalyzerClient
from .exceptions import (
    AnalysisError,
    AnalyzerError,
    ConfigurationError,
    LLMAnalysisError,
    ParsingError,
    PatternDetectionError,
    ProviderNotFoundError,
    ReportError,
    ReportFormatError,
)
from .models import Analysis, AnalyzerConfig, CodeIssue, MetricResult, ProjectAnalysis
from .testing import (
    TestResult,
    TestSuiteResult,
    CoverageReport,
    TestDiscoverer,
    TestExecutor,
    TestAnalyzer,
)

__all__ = [
    # Client
    "AnalyzerClient",
    "AsyncAnalyzerClient",
    # Models
    "Analysis",
    "AnalyzerConfig",
    "CodeIssue",
    "MetricResult",
    "ProjectAnalysis",
    # Testing Framework
    "TestResult",
    "TestSuiteResult",
    "CoverageReport",
    "TestDiscoverer",
    "TestExecutor",
    "TestAnalyzer",
    # Exceptions
    "AnalyzerError",
    "AnalysisError",
    "ConfigurationError",
    "ParsingError",
    "PatternDetectionError",
    "ReportError",
    "ReportFormatError",
    "ProviderNotFoundError",
    "LLMAnalysisError",
]
