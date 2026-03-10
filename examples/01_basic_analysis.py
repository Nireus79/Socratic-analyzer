"""Basic code analysis example."""

from socratic_analyzer import AnalyzerClient, AnalyzerConfig

# Sample Python code to analyze
sample_code = '''
"""A calculator module."""

def add(x, y):
    """Add two numbers."""
    return x + y


def complex_calculation(a, b, c):
    """Calculate something complex."""
    if a > 0:
        if b > 0:
            if c > 0:
                if a > 100:
                    if b > 100:
                        if c > 100:
                            return a + b + c
    return 0


class Calculator:
    """A simple calculator class."""

    def multiply(self, x, y):
        result = x * y
        return result

    def divide(self, x, y):
        if y == 0:
            return None
        return x / y
'''


def main() -> None:
    """Run basic analysis example."""
    print("=" * 80)
    print("SOCRATIC ANALYZER - BASIC EXAMPLE")
    print("=" * 80)
    print()

    # Create analyzer with default config
    analyzer = AnalyzerClient()

    # Analyze the code
    print("Analyzing code...")
    analysis = analyzer.analyze_code(sample_code, "calculator.py")
    print()

    # Print summary
    print("ANALYSIS SUMMARY")
    print("-" * 80)
    print(f"File: {analysis.file_path}")
    print(f"File size: {analysis.file_size:,} bytes")
    print(f"Total issues: {analysis.total_issues}")
    print(f"  - Critical: {analysis.critical_issues}")
    print(f"  - High: {analysis.high_issues}")
    print()

    # Print issues
    if analysis.issues:
        print("DETECTED ISSUES")
        print("-" * 80)
        for issue in analysis.issues:
            severity = f"[{issue.severity.upper()}]"
            print(f"{severity:10} {issue.location}")
            print(f"           {issue.message}")
            if issue.suggestion:
                print(f"           SUGGESTION: {issue.suggestion}")
            print()
    else:
        print("No issues found!")
        print()

    # Print metrics
    if analysis.metrics:
        print("CODE METRICS")
        print("-" * 80)
        for metric in analysis.metrics:
            indicator = "[OK]" if metric.status == "ok" else "[!]"
            print(f"{indicator:5} {metric.name:25} {metric.value:10.1f}")
        print()

    # Print patterns
    if analysis.patterns:
        print("DETECTED PATTERNS")
        print("-" * 80)
        for pattern in analysis.patterns:
            print(f"• {pattern}")
        print()

    # Get recommendations
    print("RECOMMENDATIONS")
    print("-" * 80)
    recommendations = analyzer.get_recommendations(analysis)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    print()

    # Generate reports in different formats
    print("GENERATING REPORTS")
    print("-" * 80)

    # Text report
    print("\n1. TEXT REPORT (excerpt):")
    print("-" * 40)
    text_report = analyzer.generate_report(analysis, format="text")
    # Print first 50 lines
    lines = text_report.split("\n")[:30]
    print("\n".join(lines))
    print("... (truncated)")

    # JSON report
    print("\n2. JSON REPORT (excerpt):")
    print("-" * 40)
    json_report = analyzer.generate_report(analysis, format="json")
    # Print first 30 lines
    lines = json_report.split("\n")[:15]
    print("\n".join(lines))
    print("... (truncated)")

    # Markdown report
    print("\n3. MARKDOWN REPORT (excerpt):")
    print("-" * 40)
    md_report = analyzer.generate_report(analysis, format="markdown")
    # Print first 30 lines
    lines = md_report.split("\n")[:20]
    print("\n".join(lines))
    print("... (truncated)")

    print()
    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
