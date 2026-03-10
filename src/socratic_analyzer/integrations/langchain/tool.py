"""LangChain tool integration for Socratic Analyzer."""

from typing import Dict, Any, Optional, Union

try:
    from langchain.tools import BaseTool
    from langchain.callbacks.manager import CallbackManagerToolRun
except ImportError:
    # Fallback for newer LangChain versions
    try:
        from langchain_core.tools import BaseTool
        from langchain_core.callbacks.manager import CallbackManagerToolRun
    except ImportError:
        BaseTool = object  # type: ignore
        CallbackManagerToolRun = None  # type: ignore

from socratic_analyzer.client import AnalyzerClient
from socratic_analyzer.models import AnalyzerConfig
from socratic_analyzer.utils.quality_scorer import QualityScorer


class SocraticAnalyzerTool(BaseTool):
    """LangChain tool for code analysis using Socratic Analyzer.

    Integrates with LangChain agents and chains for automated code analysis,
    quality checking, and recommendations.
    """

    name: str = "socratic_analyzer"
    description: str = (
        "Analyzes Python code for quality issues, design patterns, code smells, "
        "performance problems, and provides quality score (0-100). "
        "Input should be Python source code as a string."
    )

    client: AnalyzerClient

    def __init__(
        self,
        max_complexity: int = 10,
        include_metrics: bool = True,
        analyze_types: bool = True,
        analyze_docstrings: bool = True,
        **kwargs: Any,
    ):
        """Initialize analyzer tool.

        Args:
            max_complexity: Maximum allowed cyclomatic complexity
            include_metrics: Whether to include code metrics
            analyze_types: Whether to analyze type hints
            analyze_docstrings: Whether to analyze docstrings
            **kwargs: Additional arguments for BaseTool
        """
        super().__init__(**kwargs)
        config = AnalyzerConfig(
            max_complexity=max_complexity,
            include_metrics=include_metrics,
            analyze_types=analyze_types,
            analyze_docstrings=analyze_docstrings,
        )
        self.client = AnalyzerClient(config)

    def _run(
        self,
        code: str,
        run_manager: Optional[CallbackManagerToolRun] = None,
    ) -> str:
        """Run the tool synchronously.

        Args:
            code: Python source code to analyze
            run_manager: Callback manager for tool run

        Returns:
            Analysis results as formatted string
        """
        try:
            analysis = self.client.analyze_code(code, "langchain_input.py")
            quality_report = QualityScorer.create_quality_report(analysis)

            # Format results for LangChain
            result_lines = [
                f"Quality Score: {quality_report['overall_score']}/100 ({quality_report['rating']})",
                f"Total Issues: {quality_report['issue_count']}",
                f"  - Critical: {quality_report['critical_issues']}",
                f"  - High: {quality_report['high_issues']}",
                f"  - Medium: {quality_report['medium_issues']}",
                f"  - Low: {quality_report['low_issues']}",
            ]

            if analysis.patterns:
                result_lines.append(f"Patterns Detected: {', '.join(analysis.patterns)}")

            if quality_report["suggestions"]:
                result_lines.append("Suggestions:")
                for suggestion in quality_report["suggestions"]:
                    result_lines.append(f"  - {suggestion}")

            if quality_report["issue_count"] > 0 and quality_report["issue_count"] <= 5:
                result_lines.append("\nTop Issues:")
                for issue in analysis.issues[:5]:
                    result_lines.append(
                        f"  - {issue.severity.upper()}: {issue.message} "
                        f"({issue.location})"
                    )

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error analyzing code: {str(e)}"

    async def _arun(
        self,
        code: str,
        run_manager: Optional[Any] = None,
    ) -> str:
        """Run the tool asynchronously.

        Args:
            code: Python source code to analyze
            run_manager: Callback manager for tool run

        Returns:
            Analysis results as formatted string
        """
        # For now, run synchronously in executor
        return self._run(code, run_manager)


class SocraticAnalyzerQualityTool(BaseTool):
    """LangChain tool for getting quality score (0-100)."""

    name: str = "socratic_quality_score"
    description: str = (
        "Get quality score (0-100) for Python code. "
        "Input should be Python source code as a string. "
        "Returns a score where 100 is perfect and 0 is critical issues."
    )

    client: AnalyzerClient

    def __init__(self, **kwargs: Any):
        """Initialize quality score tool."""
        super().__init__(**kwargs)
        self.client = AnalyzerClient()

    def _run(self, code: str, run_manager: Optional[CallbackManagerToolRun] = None) -> str:
        """Run the tool synchronously."""
        try:
            analysis = self.client.analyze_code(code)
            quality_report = QualityScorer.create_quality_report(analysis)
            score = quality_report["overall_score"]
            rating = quality_report["rating"]
            return f"Quality Score: {score}/100 ({rating})"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, code: str, run_manager: Optional[Any] = None) -> str:
        """Run the tool asynchronously."""
        return self._run(code, run_manager)


class SocraticAnalyzerIssuesTool(BaseTool):
    """LangChain tool for getting detailed issues list."""

    name: str = "socratic_detect_issues"
    description: str = (
        "Detect issues in Python code and return detailed list. "
        "Input should be Python source code as a string. "
        "Returns list of issues with severity levels and suggestions."
    )

    client: AnalyzerClient

    def __init__(self, **kwargs: Any):
        """Initialize issues detection tool."""
        super().__init__(**kwargs)
        self.client = AnalyzerClient()

    def _run(self, code: str, run_manager: Optional[CallbackManagerToolRun] = None) -> str:
        """Run the tool synchronously."""
        try:
            analysis = self.client.analyze_code(code)

            if not analysis.issues:
                return "No issues detected. Code quality is excellent!"

            result_lines = [f"Found {len(analysis.issues)} issues:\n"]

            for i, issue in enumerate(analysis.issues, 1):
                result_lines.append(
                    f"{i}. [{issue.severity.upper()}] {issue.message} "
                    f"at {issue.location}"
                )
                if issue.suggestion:
                    result_lines.append(f"   Suggestion: {issue.suggestion}")

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, code: str, run_manager: Optional[Any] = None) -> str:
        """Run the tool asynchronously."""
        return self._run(code, run_manager)


class SocraticAnalyzerRecommendationsTool(BaseTool):
    """LangChain tool for getting improvement recommendations."""

    name: str = "socratic_recommendations"
    description: str = (
        "Get actionable recommendations to improve Python code. "
        "Input should be Python source code as a string. "
        "Returns prioritized list of improvements."
    )

    client: AnalyzerClient

    def __init__(self, **kwargs: Any):
        """Initialize recommendations tool."""
        super().__init__(**kwargs)
        self.client = AnalyzerClient()

    def _run(self, code: str, run_manager: Optional[CallbackManagerToolRun] = None) -> str:
        """Run the tool synchronously."""
        try:
            analysis = self.client.analyze_code(code)
            recommendations = self.client.get_recommendations(analysis)

            result_lines = ["Recommendations:\n"]
            for i, rec in enumerate(recommendations, 1):
                result_lines.append(f"{i}. {rec}")

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, code: str, run_manager: Optional[Any] = None) -> str:
        """Run the tool asynchronously."""
        return self._run(code, run_manager)


def create_analyzer_tools() -> list:
    """Create a list of all Socratic Analyzer tools for LangChain.

    Returns:
        List of tool instances ready to use in LangChain
    """
    return [
        SocraticAnalyzerTool(),
        SocraticAnalyzerQualityTool(),
        SocraticAnalyzerIssuesTool(),
        SocraticAnalyzerRecommendationsTool(),
    ]
