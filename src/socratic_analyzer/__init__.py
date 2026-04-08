"""Socratic Analyzer - Production-grade code analysis package."""

__version__ = "0.1.0"
__author__ = "Socratic Analyzer"
__email__ = "info@socratic-analyzer.dev"

from .async_client import AsyncAnalyzerClient
from .client import AnalyzerClient
from .debugging import (
    DebugEvent,
    ExecutionProfiler,
    WorkflowDebugger,
    WorkflowDebugTrace,
    WorkflowValidator,
)
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
from .extraction.code_extractor import CodeExtractor
from .models import Analysis, AnalyzerConfig, CodeIssue, MetricResult, ProjectAnalysis
from .parsing.code_parser import CodeParser
from .testing import (
    ABTestingFramework,
    CoverageReport,
    ExperimentMetrics,
    ExperimentResult,
    ExperimentStatus,
    HypothesisResult,
    TestAnalyzer,
    TestDiscoverer,
    TestExecutor,
    TestResult,
    TestSuiteResult,
    Variant,
    VariantAssignment,
)

__all__ = [
    # Client
    "AnalyzerClient",
    "AsyncAnalyzerClient",
    # Code Analysis
    "CodeParser",
    "CodeExtractor",
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
    # A/B Testing
    "ABTestingFramework",
    "ExperimentResult",
    "ExperimentStatus",
    "ExperimentMetrics",
    "HypothesisResult",
    "Variant",
    "VariantAssignment",
    # Workflow Debugging
    "WorkflowDebugger",
    "ExecutionProfiler",
    "WorkflowValidator",
    "DebugEvent",
    "WorkflowDebugTrace",
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
