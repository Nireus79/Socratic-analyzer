"""Custom exceptions for Socratic Analyzer."""


class AnalyzerError(Exception):
    """Base exception for analyzer operations."""

    pass


class AnalysisError(AnalyzerError):
    """Error during code analysis."""

    pass


class ConfigurationError(AnalyzerError):
    """Error in analyzer configuration."""

    pass


class ParsingError(AnalysisError):
    """Error parsing code."""

    pass


class PatternDetectionError(AnalysisError):
    """Error detecting patterns."""

    pass


class ReportError(AnalyzerError):
    """Error generating report."""

    pass


class ReportFormatError(ReportError):
    """Unsupported report format."""

    pass


class ProviderNotFoundError(AnalyzerError):
    """Provider not found."""

    pass


class LLMAnalysisError(AnalyzerError):
    """Error in LLM-powered analysis."""

    pass
