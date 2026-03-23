"""
Socratic Analyzer - Production-grade code analysis with LLM-powered insights

Provides intelligent code analysis with Claude AI for the Socratic platform.
"""

__version__ = "0.1.0"

from .analyzer import CodeAnalyzer
from .insights import InsightGenerator
from .metrics import QualityMetrics

__all__ = [
    "CodeAnalyzer",
    "InsightGenerator",
    "QualityMetrics",
]
