"""Main analyzer client interface."""

from typing import List, Optional

from socratic_analyzer.analyzers.complexity import ComplexityAnalyzer
from socratic_analyzer.analyzers.imports import ImportAnalyzer
from socratic_analyzer.analyzers.metrics import MetricsAnalyzer
from socratic_analyzer.analyzers.static import StaticAnalyzer
from socratic_analyzer.models import Analysis, AnalyzerConfig, CodeIssue, MetricResult


class AnalyzerClient:
    """Main analyzer client interface.

    Provides a unified interface for analyzing Python code with multiple
    specialized analyzers.
    """

    def __init__(self, config: Optional[AnalyzerConfig] = None) -> None:
        """Initialize analyzer client.

        Args:
            config: AnalyzerConfig object. If None, uses default configuration.
        """
        self.config = config or AnalyzerConfig()

        # Initialize analyzers
        self._static_analyzer = StaticAnalyzer()
        self._complexity_analyzer = ComplexityAnalyzer(
            max_complexity=self.config.max_complexity
        )
        self._metrics_analyzer = MetricsAnalyzer()
        self._import_analyzer = ImportAnalyzer()

    def analyze_file(self, file_path: str) -> Analysis:
        """Analyze a single Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            Analysis object with results

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {e}")

        return self.analyze_code(code, file_path)

    def analyze_code(self, code: str, file_path: str = "unknown.py") -> Analysis:
        """Analyze Python code.

        Args:
            code: Python source code
            file_path: Path to file (for reporting, optional)

        Returns:
            Analysis object with results
        """
        # Get file size
        file_size = len(code.encode("utf-8"))

        # Collect all issues
        issues = []

        # Run static analysis
        if self.config.analyze_types or self.config.analyze_docstrings:
            issues.extend(self._static_analyzer.analyze(code, file_path))

        # Run complexity analysis
        issues.extend(self._complexity_analyzer.analyze(code, file_path))

        # Run import analysis
        issues.extend(self._import_analyzer.analyze(code, file_path))

        # Collect metrics
        metrics = []
        if self.config.include_metrics:
            metrics.extend(self._metrics_analyzer.calculate_metrics(code))

        # Detect patterns
        patterns = self._detect_patterns(code, issues)

        # Create analysis
        analysis = Analysis(
            file_path=file_path,
            file_size=file_size,
            language="python",
            issues=issues,
            metrics=metrics,
            patterns=patterns,
        )

        return analysis

    def _detect_patterns(self, code: str, issues: List[CodeIssue]) -> List[str]:
        """Detect code patterns from issues and code.

        Args:
            code: Source code
            issues: Detected issues

        Returns:
            List of detected patterns
        """
        patterns = []

        # Extract patterns from issue types
        issue_types = set(i.issue_type for i in issues)

        if "complexity" in issue_types:
            patterns.append("High cyclomatic complexity detected")

        if any("unused" in i.message.lower() for i in issues):
            patterns.append("Unused variables detected")

        if any("long" in i.message.lower() for i in issues):
            patterns.append("Long lines detected")

        if any("docstring" in i.message.lower() for i in issues):
            patterns.append("Missing documentation detected")

        if any("wildcard" in i.message.lower() for i in issues):
            patterns.append("Wildcard imports detected")

        if any("nesting" in i.message.lower() for i in issues):
            patterns.append("Deep nesting detected")

        # Check for specific code patterns
        if "class " in code and "def __init__" in code:
            patterns.append("Object-oriented design detected")

        if "@property" in code:
            patterns.append("Property decorators used")

        if "async def" in code:
            patterns.append("Async/await usage detected")

        if "try:" in code and "except" in code:
            patterns.append("Exception handling detected")

        return patterns

    def generate_report(
        self, analysis: Analysis, format: str = "text"
    ) -> str:
        """Generate formatted report.

        Args:
            analysis: Analysis object
            format: Report format ("text", "json", "markdown")

        Returns:
            Formatted report string

        Raises:
            ValueError: If format is not supported
        """
        if format == "json":
            return self._format_json(analysis)
        elif format == "markdown":
            return self._format_markdown(analysis)
        elif format == "text":
            return self._format_text(analysis)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _format_text(self, analysis: Analysis) -> str:
        """Format analysis as text report.

        Args:
            analysis: Analysis object

        Returns:
            Text report
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"Analysis Report: {analysis.file_path}")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append(f"  File size: {analysis.file_size:,} bytes")
        lines.append(f"  Language: {analysis.language}")
        lines.append(f"  Total issues: {analysis.total_issues}")
        lines.append(f"    - Critical: {analysis.critical_issues}")
        lines.append(f"    - High: {analysis.high_issues}")
        lines.append("")

        # Issues
        if analysis.issues:
            lines.append("ISSUES")
            for issue in analysis.issues:
                severity_label = issue.severity.upper()
                lines.append(f"  {severity_label}: {issue.location}")
                lines.append(f"    {issue.message}")
                if issue.suggestion:
                    lines.append(f"    Suggestion: {issue.suggestion}")
                lines.append("")
        else:
            lines.append("No issues found!")
            lines.append("")

        # Metrics
        if analysis.metrics:
            lines.append("METRICS")
            for metric in analysis.metrics:
                status_indicator = "[OK]" if metric.status == "ok" else "[!]"
                lines.append(
                    f"  {status_indicator} {metric.name}: {metric.value:.1f}"
                )
                if metric.description:
                    lines.append(f"    {metric.description}")
            lines.append("")

        # Patterns
        if analysis.patterns:
            lines.append("PATTERNS DETECTED")
            for pattern in analysis.patterns:
                lines.append(f"  - {pattern}")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)

    def _format_json(self, analysis: Analysis) -> str:
        """Format analysis as JSON report.

        Args:
            analysis: Analysis object

        Returns:
            JSON report
        """
        import json
        from datetime import datetime

        data = {
            "file_path": analysis.file_path,
            "file_size": analysis.file_size,
            "language": analysis.language,
            "timestamp": analysis.timestamp.isoformat(),
            "summary": {
                "total_issues": analysis.total_issues,
                "critical_issues": analysis.critical_issues,
                "high_issues": analysis.high_issues,
            },
            "issues": [
                {
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "location": issue.location,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                }
                for issue in analysis.issues
            ],
            "metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "status": metric.status,
                    "description": metric.description,
                }
                for metric in analysis.metrics
            ],
            "patterns": analysis.patterns,
        }

        return json.dumps(data, indent=2)

    def _format_markdown(self, analysis: Analysis) -> str:
        """Format analysis as Markdown report.

        Args:
            analysis: Analysis object

        Returns:
            Markdown report
        """
        lines = []
        lines.append(f"# Analysis Report: {analysis.file_path}")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append(
            f"- **File size**: {analysis.file_size:,} bytes"
        )
        lines.append(f"- **Language**: {analysis.language}")
        lines.append(f"- **Issues**: {analysis.total_issues}")
        lines.append(f"  - Critical: {analysis.critical_issues}")
        lines.append(f"  - High: {analysis.high_issues}")
        lines.append("")

        # Issues by severity
        if analysis.issues:
            lines.append("## Issues")

            critical = [i for i in analysis.issues if i.severity == "critical"]
            if critical:
                lines.append("### Critical")
                for issue in critical:
                    lines.append(f"- **{issue.location}**: {issue.message}")
                    if issue.suggestion:
                        lines.append(f"  - Suggestion: {issue.suggestion}")
                lines.append("")

            high = [i for i in analysis.issues if i.severity == "high"]
            if high:
                lines.append("### High")
                for issue in high:
                    lines.append(f"- **{issue.location}**: {issue.message}")
                lines.append("")

            medium = [i for i in analysis.issues if i.severity == "medium"]
            if medium:
                lines.append("### Medium")
                for issue in medium:
                    lines.append(f"- {issue.location}: {issue.message}")
                lines.append("")

            low = [i for i in analysis.issues if i.severity in ("low", "info")]
            if low:
                lines.append("### Low/Info")
                for issue in low:
                    lines.append(f"- {issue.location}: {issue.message}")
                lines.append("")
        else:
            lines.append("## Issues")
            lines.append("No issues found! ✅")
            lines.append("")

        # Metrics
        if analysis.metrics:
            lines.append("## Metrics")
            for metric in analysis.metrics:
                lines.append(
                    f"- **{metric.name}**: {metric.value:.1f} "
                    f"(status: {metric.status})"
                )
            lines.append("")

        # Patterns
        if analysis.patterns:
            lines.append("## Patterns Detected")
            for pattern in analysis.patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        return "\n".join(lines)

    def get_recommendations(self, analysis: Analysis) -> List[str]:
        """Get actionable recommendations from analysis.

        Args:
            analysis: Analysis object

        Returns:
            List of recommendations
        """
        recommendations = []

        # Critical issues
        critical_count = analysis.critical_issues
        if critical_count > 0:
            recommendations.append(
                f"[CRITICAL] Fix {critical_count} critical issue(s) immediately"
            )

        # High severity issues
        high_count = analysis.high_issues
        if high_count > 0:
            recommendations.append(
                f"[HIGH] Address {high_count} high-severity issue(s)"
            )

        # Complexity issues
        complexity_issues = [i for i in analysis.issues if i.issue_type == "complexity"]
        if complexity_issues:
            recommendations.append(
                "[COMPLEXITY] Refactor complex functions (consider breaking into smaller functions)"
            )

        # Documentation issues
        doc_issues = [
            i for i in analysis.issues if "docstring" in i.message.lower()
        ]
        if doc_issues:
            recommendations.append(
                f"[DOCS] Add documentation to {len(doc_issues)} item(s)"
            )

        # Style issues
        style_issues = [i for i in analysis.issues if i.issue_type == "style"]
        if len(style_issues) > 5:
            recommendations.append(
                "[STYLE] Address multiple style issues (consider using a code formatter)"
            )

        # Maintainability
        if analysis.metrics:
            maintainability = next(
                (m for m in analysis.metrics if m.name == "maintainability_index"),
                None,
            )
            if maintainability and maintainability.value < 50:
                recommendations.append(
                    "[MAINTAINABILITY] Maintainability is low - consider refactoring"
                )

        if not recommendations:
            recommendations.append("[OK] Code quality is good!")

        return recommendations
