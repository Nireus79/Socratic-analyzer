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
