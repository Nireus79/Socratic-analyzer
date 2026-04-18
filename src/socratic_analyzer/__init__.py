"""Socratic Analyzer - Production-grade code and document analysis."""

__version__ = "0.2.0"

from .async_client import AsyncAnalyzerClient
from .client import AnalyzerClient
from .debugging import (
    DebugEvent,
    ExecutionProfiler,
    WorkflowDebugger,
    WorkflowDebugTrace,
    WorkflowValidator,
)
from .document_analyzer import (
    AdaptiveDocumentLoader,
    Document,
    DocumentAnalyzer,
    DocumentAnalysisResult,
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
    # Document Analysis
    "DocumentAnalyzer",
    "AdaptiveDocumentLoader",
    "Document",
    "DocumentAnalysisResult",
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
