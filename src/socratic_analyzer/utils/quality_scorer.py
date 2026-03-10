"""Quality scoring system for code analysis results."""

from typing import List

from socratic_analyzer.models import Analysis, MetricResult


class QualityScorer:
    """Calculate overall code quality score."""

    # Severity weights for quality calculation
    SEVERITY_WEIGHTS = {
        "critical": 50,
        "high": 30,
        "medium": 15,
        "low": 5,
        "info": 1,
    }

    # Issue type weights
    ISSUE_TYPE_WEIGHTS = {
        "syntax": 50,
        "complexity": 25,
        "performance": 20,
        "smell": 15,
        "style": 10,
        "pattern": 5,
        "info": 2,
    }

    @classmethod
    def calculate_quality_score(cls, analysis: Analysis) -> float:
        """Calculate overall quality score (0-100).

        Args:
            analysis: Analysis object with results

        Returns:
            Quality score from 0-100
        """
        if not analysis.issues:
            return 100.0

        # Start with 100
        score = 100.0

        # Deduct points for each issue
        for issue in analysis.issues:
            severity_weight = cls.SEVERITY_WEIGHTS.get(issue.severity, 5)
            issue_type_weight = cls.ISSUE_TYPE_WEIGHTS.get(issue.issue_type, 10)
            deduction = (severity_weight * issue_type_weight) / 100

            score -= deduction

        # Cap at 0
        return max(0.0, score)

    @classmethod
    def get_quality_rating(cls, score: float) -> str:
        """Get quality rating based on score.

        Args:
            score: Quality score (0-100)

        Returns:
            Quality rating
        """
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 50:
            return "Poor"
        else:
            return "Critical"

    @classmethod
    def get_quality_color(cls, score: float) -> str:
        """Get color indicator for quality score.

        Args:
            score: Quality score (0-100)

        Returns:
            Color indicator
        """
        if score >= 90:
            return "green"
        elif score >= 80:
            return "blue"
        elif score >= 70:
            return "yellow"
        elif score >= 60:
            return "orange"
        else:
            return "red"

    @classmethod
    def calculate_issue_score(cls, analysis: Analysis) -> float:
        """Calculate score based on issues only.

        Args:
            analysis: Analysis object

        Returns:
            Issue-based score
        """
        if not analysis.issues:
            return 100.0

        critical = sum(1 for i in analysis.issues if i.severity == "critical")
        high = sum(1 for i in analysis.issues if i.severity == "high")
        medium = sum(1 for i in analysis.issues if i.severity == "medium")

        # Deduct points
        score = 100.0
        score -= critical * 20
        score -= high * 10
        score -= medium * 5

        return max(0.0, score)

    @classmethod
    def calculate_metrics_score(cls, analysis: Analysis) -> float:
        """Calculate score based on metrics.

        Args:
            analysis: Analysis object

        Returns:
            Metrics-based score
        """
        if not analysis.metrics:
            return 100.0

        scores = []

        for metric in analysis.metrics:
            if metric.status == "ok":
                scores.append(100.0)
            else:
                # Calculate based on how far from threshold
                if metric.threshold is not None and metric.threshold > 0:
                    deviation = abs(metric.value - metric.threshold) / metric.threshold
                    score = max(0.0, 100.0 - (deviation * 100))
                    scores.append(score)

        if not scores:
            return 100.0

        return sum(scores) / len(scores)

    @classmethod
    def get_improvement_suggestions(cls, analysis: Analysis) -> List[str]:
        """Get suggestions for code improvement.

        Args:
            analysis: Analysis object

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Count issues by severity
        critical_count = sum(1 for i in analysis.issues if i.severity == "critical")
        high_count = sum(1 for i in analysis.issues if i.severity == "high")
        medium_count = sum(1 for i in analysis.issues if i.severity == "medium")

        # Generate suggestions
        if critical_count > 0:
            suggestions.append(
                f"Fix {critical_count} critical issue(s) immediately - these may break functionality"
            )

        if high_count > 0:
            suggestions.append(f"Address {high_count} high-severity issue(s) soon")

        complexity_issues = sum(1 for i in analysis.issues if i.issue_type == "complexity")
        if complexity_issues > 0:
            suggestions.append(
                f"Refactor {complexity_issues} complex function(s) into smaller units"
            )

        performance_issues = sum(
            1 for i in analysis.issues if i.issue_type == "performance"
        )
        if performance_issues > 0:
            suggestions.append(
                f"Optimize {performance_issues} performance issue(s) for better efficiency"
            )

        smell_issues = sum(1 for i in analysis.issues if i.issue_type == "smell")
        if smell_issues > 0:
            suggestions.append(f"Address {smell_issues} code smell(s) for maintainability")

        # Check metrics
        if analysis.metrics:
            for metric in analysis.metrics:
                if metric.status != "ok" and metric.name == "maintainability_index":
                    suggestions.append(
                        "Improve maintainability by reducing complexity and improving documentation"
                    )

        if not suggestions:
            suggestions.append("Code quality is excellent - maintain current standards")

        return suggestions

    @classmethod
    def create_quality_report(cls, analysis: Analysis) -> dict:
        """Create comprehensive quality report.

        Args:
            analysis: Analysis object

        Returns:
            Dictionary with quality metrics
        """
        overall_score = cls.calculate_quality_score(analysis)
        issue_score = cls.calculate_issue_score(analysis)
        metrics_score = cls.calculate_metrics_score(analysis)

        return {
            "overall_score": round(overall_score, 1),
            "issue_score": round(issue_score, 1),
            "metrics_score": round(metrics_score, 1),
            "rating": cls.get_quality_rating(overall_score),
            "color": cls.get_quality_color(overall_score),
            "issue_count": len(analysis.issues),
            "critical_issues": sum(1 for i in analysis.issues if i.severity == "critical"),
            "high_issues": sum(1 for i in analysis.issues if i.severity == "high"),
            "medium_issues": sum(1 for i in analysis.issues if i.severity == "medium"),
            "low_issues": sum(1 for i in analysis.issues if i.severity == "low"),
            "suggestions": cls.get_improvement_suggestions(analysis),
        }
