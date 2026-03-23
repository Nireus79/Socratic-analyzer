"""
Insight generation from code analysis.
"""

import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class InsightData(BaseModel):
    """Data structure for generated insights."""

    category: str = Field(..., description="Category of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    severity: str = Field(default="info", description="Severity level (info, warning, critical)")
    actionable: bool = Field(default=True, description="Whether insight is actionable")


class InsightGenerator:
    """
    Generate actionable insights from code analysis results.

    Transforms raw analysis data into meaningful, actionable insights
    that developers can use to improve their code.
    """

    def __init__(self):
        """Initialize the insight generator."""
        self.categories = [
            "code_quality",
            "performance",
            "security",
            "maintainability",
            "testing",
            "documentation"
        ]

    def generate_insights(self, analysis_data: Dict[str, Any]) -> List[InsightData]:
        """
        Generate insights from analysis data.

        Args:
            analysis_data: Analysis results dictionary

        Returns:
            List of insight objects
        """
        insights = []

        # Extract issues and convert to insights
        for issue in analysis_data.get("issues", []):
            insights.append(InsightData(
                category="code_quality",
                title="Code Quality Issue",
                description=issue,
                severity="warning"
            ))

        # Extract improvements
        for improvement in analysis_data.get("improvements", []):
            insights.append(InsightData(
                category="maintainability",
                title="Improvement Opportunity",
                description=improvement,
                severity="info"
            ))

        # Extract security concerns
        for concern in analysis_data.get("security_concerns", []):
            insights.append(InsightData(
                category="security",
                title="Security Concern",
                description=concern,
                severity="critical"
            ))

        # Extract performance concerns
        for concern in analysis_data.get("performance_concerns", []):
            insights.append(InsightData(
                category="performance",
                title="Performance Issue",
                description=concern,
                severity="warning"
            ))

        logger.info(f"Generated {len(insights)} insights from analysis data")
        return insights

    def prioritize_insights(self, insights: List[InsightData]) -> List[InsightData]:
        """
        Prioritize insights by severity and actionability.

        Args:
            insights: List of insights to prioritize

        Returns:
            Prioritized list of insights
        """
        severity_order = {"critical": 0, "warning": 1, "info": 2}

        return sorted(
            insights,
            key=lambda x: (
                severity_order.get(x.severity, 3),
                not x.actionable
            )
        )

    def summarize_insights(self, insights: List[InsightData]) -> Dict[str, int]:
        """
        Summarize insights by category.

        Args:
            insights: List of insights

        Returns:
            Dictionary with insight counts by category
        """
        summary = {category: 0 for category in self.categories}
        for insight in insights:
            if insight.category in summary:
                summary[insight.category] += 1
        return summary
