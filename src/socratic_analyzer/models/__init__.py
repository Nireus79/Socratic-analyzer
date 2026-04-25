"""Data models extracted from Socrates monolith."""

# Import models from their owning libraries
from socratic_conflict import ConflictInfo
from socratic_maturity import CategoryScore, PhaseMaturity, MaturityEvent

# Local models
from .project import ProjectContext
from .role import TeamMemberRole
from .workflow import WorkflowDefinition, WorkflowEdge, WorkflowNode, WorkflowPath

__all__ = [
    "ConflictInfo",
    "CategoryScore",
    "PhaseMaturity",
    "MaturityEvent",
    "ProjectContext",
    "TeamMemberRole",
    "WorkflowDefinition",
    "WorkflowEdge",
    "WorkflowNode",
    "WorkflowPath",
]
