from __future__ import annotations

"""
Socratic Analyzer - Analysis and Monitoring

Extracted from Socrates v1.3.3
"""

# Core analysis modules
from .core import (
    InsightCategorizer,
    WorkflowCostCalculator,
    WorkflowPathFinder,
    WorkflowRiskCalculator,
    get_phase_categories,
)

# Data models
from .models import (
    CategoryScore,
    PhaseMaturity,
    ProjectContext,
    TeamMemberRole,
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowNode,
    WorkflowPath,
)

# Utilities
from .monitoring import TokenUsage
from .utils import DependencyValidator, SyntaxValidator, TestExecutor

__version__ = "0.1.6"
__all__ = [
    # Core analysis
    "InsightCategorizer",
    "WorkflowCostCalculator",
    "WorkflowPathFinder",
    "WorkflowRiskCalculator",
    "get_phase_categories",
    # Data models
    "CategoryScore",
    "PhaseMaturity",
    "ProjectContext",
    "TeamMemberRole",
    "WorkflowDefinition",
    "WorkflowEdge",
    "WorkflowNode",
    "WorkflowPath",
    # Utilities
    "TokenUsage",
    "DependencyValidator",
    "SyntaxValidator",
    "TestExecutor",
]
