"""Openclaw skill for Socratic Analyzer."""

from typing import Dict, List, Optional, Any

from socratic_analyzer.client import AnalyzerClient
from socratic_analyzer.models import AnalyzerConfig, Analysis
from socratic_analyzer.utils.quality_scorer import QualityScorer


class SocraticAnalyzerSkill:
    """Openclaw skill for code analysis using Socratic Analyzer.

    Provides analysis of Python code with design patterns, code smells,
    performance issues, and quality scoring.
    """

    def __init__(self, max_complexity: int = 10, include_metrics: bool = True):
        """Initialize analyzer skill.

        Args:
            max_complexity: Maximum allowed cyclomatic complexity
            include_metrics: Whether to include code metrics in analysis
        """
        config = AnalyzerConfig(
            max_complexity=max_complexity,
            include_metrics=include_metrics,
            analyze_types=True,
            analyze_docstrings=True,
        )
        self.client = AnalyzerClient(config)

    def analyze_code(self, code: str, file_path: str = "unknown.py") -> Dict[str, Any]:
        """Analyze Python code.

        Args:
            code: Python source code to analyze
            file_path: File path for reporting (optional)

        Returns:
            Dictionary with analysis results
        """
        analysis = self.client.analyze_code(code, file_path)
        return self._format_analysis_result(analysis)

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary with analysis results

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        analysis = self.client.analyze_file(file_path)
        return self._format_analysis_result(analysis)

    def analyze_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze multiple Python files.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            Dictionary with aggregated results
        """
        results = []
        total_issues = 0
        total_critical = 0
        total_high = 0
        scores = []

        for file_path in file_paths:
            try:
                analysis = self.client.analyze_file(file_path)
                results.append(self._format_analysis_result(analysis))
                total_issues += len(analysis.issues)
                total_critical += analysis.critical_issues
                total_high += analysis.high_issues

                # Calculate quality score
                quality_report = QualityScorer.create_quality_report(analysis)
                scores.append(quality_report["overall_score"])
            except (FileNotFoundError, IOError) as e:
                results.append(
                    {
                        "file_path": file_path,
                        "error": str(e),
                        "status": "failed",
                    }
                )

        # Calculate average score
        avg_score = sum(scores) / len(scores) if scores else 0.0

        return {
            "files_analyzed": len(file_paths),
            "files_successful": len(scores),
            "total_issues": total_issues,
            "critical_issues": total_critical,
            "high_issues": total_high,
            "average_quality_score": round(avg_score, 1),
            "average_rating": QualityScorer.get_quality_rating(avg_score),
            "results": results,
        }

    def get_quality_score(self, code: str, file_path: str = "unknown.py") -> float:
        """Get quality score for code (0-100).

        Args:
            code: Python source code
            file_path: File path for reporting

        Returns:
            Quality score between 0 and 100
        """
        analysis = self.client.analyze_code(code, file_path)
        quality_report = QualityScorer.create_quality_report(analysis)
        return quality_report["overall_score"]

    def get_quality_report(
        self, code: str, file_path: str = "unknown.py"
    ) -> Dict[str, Any]:
        """Get comprehensive quality report.

        Args:
            code: Python source code
            file_path: File path for reporting

        Returns:
            Dictionary with detailed quality metrics
        """
        analysis = self.client.analyze_code(code, file_path)
        return QualityScorer.create_quality_report(analysis)

    def get_recommendations(self, code: str, file_path: str = "unknown.py") -> List[str]:
        """Get actionable recommendations.

        Args:
            code: Python source code
            file_path: File path for reporting

        Returns:
            List of recommendations
        """
        analysis = self.client.analyze_code(code, file_path)
        return self.client.get_recommendations(analysis)

    def detect_patterns(self, code: str) -> List[str]:
        """Detect design patterns in code.

        Args:
            code: Python source code

        Returns:
            List of detected patterns
        """
        analysis = self.client.analyze_code(code)
        return analysis.patterns

    def detect_issues(
        self, code: str, severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Detect issues in code.

        Args:
            code: Python source code
            severity: Filter by severity (critical, high, medium, low, info)

        Returns:
            List of issues as dictionaries
        """
        analysis = self.client.analyze_code(code)

        issues = []
        for issue in analysis.issues:
            if severity is None or issue.severity == severity:
                issues.append(
                    {
                        "type": issue.issue_type,
                        "severity": issue.severity,
                        "location": issue.location,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                    }
                )

        return issues

    def generate_report(
        self, code: str, format: str = "text", file_path: str = "unknown.py"
    ) -> str:
        """Generate formatted analysis report.

        Args:
            code: Python source code
            format: Report format (text, json, markdown)
            file_path: File path for reporting

        Returns:
            Formatted report string
        """
        analysis = self.client.analyze_code(code, file_path)
        return self.client.generate_report(analysis, format=format)

    def check_quality_threshold(
        self, code: str, threshold: float = 70.0
    ) -> Dict[str, Any]:
        """Check if code meets quality threshold.

        Args:
            code: Python source code
            threshold: Quality score threshold (0-100)

        Returns:
            Dictionary with pass/fail status and details
        """
        analysis = self.client.analyze_code(code)
        quality_report = QualityScorer.create_quality_report(analysis)
        score = quality_report["overall_score"]

        return {
            "passes_threshold": score >= threshold,
            "threshold": threshold,
            "score": score,
            "rating": quality_report["rating"],
            "gap": round(threshold - score, 1) if score < threshold else 0.0,
        }

    def compare_codes(self, code1: str, code2: str) -> Dict[str, Any]:
        """Compare quality of two code samples.

        Args:
            code1: First Python code sample
            code2: Second Python code sample

        Returns:
            Comparison results
        """
        analysis1 = self.client.analyze_code(code1, "code1.py")
        analysis2 = self.client.analyze_code(code2, "code2.py")

        report1 = QualityScorer.create_quality_report(analysis1)
        report2 = QualityScorer.create_quality_report(analysis2)

        score1 = report1["overall_score"]
        score2 = report2["overall_score"]
        diff = score2 - score1

        return {
            "code1_score": score1,
            "code1_rating": report1["rating"],
            "code1_issues": report1["issue_count"],
            "code2_score": score2,
            "code2_rating": report2["rating"],
            "code2_issues": report2["issue_count"],
            "difference": round(diff, 1),
            "winner": "code2" if diff > 0 else ("code1" if diff < 0 else "tie"),
            "improvement": f"{diff:+.1f} points",
        }

    @staticmethod
    def _format_analysis_result(analysis: Analysis) -> Dict[str, Any]:
        """Format analysis result for Openclaw.

        Args:
            analysis: Analysis object

        Returns:
            Dictionary with formatted results
        """
        quality_report = QualityScorer.create_quality_report(analysis)

        return {
            "file_path": analysis.file_path,
            "file_size": analysis.file_size,
            "language": analysis.language,
            "quality_score": quality_report["overall_score"],
            "quality_rating": quality_report["rating"],
            "total_issues": quality_report["issue_count"],
            "critical_issues": quality_report["critical_issues"],
            "high_issues": quality_report["high_issues"],
            "medium_issues": quality_report["medium_issues"],
            "low_issues": quality_report["low_issues"],
            "patterns_detected": len(analysis.patterns),
            "recommendations": quality_report["suggestions"],
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
            "patterns": analysis.patterns,
            "metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "status": metric.status,
                }
                for metric in analysis.metrics
            ],
        }
