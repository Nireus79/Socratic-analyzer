"""Example: Using Socratic Analyzer as an Openclaw Skill."""

from socratic_analyzer.integrations.openclaw import SocraticAnalyzerSkill

# Sample Python code to analyze
sample_code = '''
def process_data(items, callback=None):
    """Process data items."""
    results = []
    for item in items:
        # Potential performance issue: mutable default
        processed = item * 2
        results += [processed]  # String concatenation pattern
    return results

def complex_logic(a, b, c, d, e):
    """Complex nested logic."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
    return 0
'''


def main() -> None:
    """Run Openclaw integration example."""
    print("=" * 80)
    print("SOCRATIC ANALYZER - OPENCLAW SKILL EXAMPLE")
    print("=" * 80)
    print()

    # Create analyzer skill
    skill = SocraticAnalyzerSkill()

    # Example 1: Get quality score
    print("1. QUALITY SCORE")
    print("-" * 80)
    score = skill.get_quality_score(sample_code)
    print(f"Quality Score: {score}/100")
    print()

    # Example 2: Get quality report
    print("2. COMPREHENSIVE QUALITY REPORT")
    print("-" * 80)
    report = skill.get_quality_report(sample_code)
    print(f"Score: {report['overall_score']}/100")
    print(f"Rating: {report['rating']}")
    print(f"Total Issues: {report['issue_count']}")
    print(f"  - Critical: {report['critical_issues']}")
    print(f"  - High: {report['high_issues']}")
    print(f"  - Medium: {report['medium_issues']}")
    print()

    # Example 3: Get issues
    print("3. DETECTED ISSUES")
    print("-" * 80)
    issues = skill.detect_issues(sample_code)
    for i, issue in enumerate(issues[:5], 1):  # Show first 5
        print(f"{i}. [{issue['severity'].upper()}] {issue['message']}")
        if issue['suggestion']:
            print(f"   Suggestion: {issue['suggestion']}")
    if len(issues) > 5:
        print(f"... and {len(issues) - 5} more issues")
    print()

    # Example 4: Get recommendations
    print("4. IMPROVEMENT RECOMMENDATIONS")
    print("-" * 80)
    recommendations = skill.get_recommendations(sample_code)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    print()

    # Example 5: Detect patterns
    print("5. DETECTED PATTERNS")
    print("-" * 80)
    patterns = skill.detect_patterns(sample_code)
    if patterns:
        for pattern in patterns:
            print(f"  - {pattern}")
    else:
        print("No patterns detected")
    print()

    # Example 6: Check quality threshold
    print("6. QUALITY THRESHOLD CHECK")
    print("-" * 80)
    threshold_result = skill.check_quality_threshold(sample_code, threshold=75.0)
    status = "PASS" if threshold_result["passes_threshold"] else "FAIL"
    print(f"Threshold: {threshold_result['threshold']}/100")
    print(f"Actual Score: {threshold_result['score']}/100")
    print(f"Status: {status}")
    if threshold_result['gap'] > 0:
        print(f"Gap: {threshold_result['gap']} points below threshold")
    print()

    # Example 7: Compare codes
    print("7. COMPARE TWO CODE SAMPLES")
    print("-" * 80)
    better_code = '''
def process_items(items):
    """Process items efficiently."""
    return [item * 2 for item in items]

def simple_logic(x):
    """Simple logic."""
    return x * 2 if x > 0 else 0
'''
    comparison = skill.compare_codes(sample_code, better_code)
    print(f"Original Code Score: {comparison['code1_score']}/100 ({comparison['code1_rating']})")
    print(f"Improved Code Score: {comparison['code2_score']}/100 ({comparison['code2_rating']})")
    print(f"Improvement: {comparison['improvement']}")
    print(f"Winner: {comparison['winner'].upper()}")
    print()

    # Example 8: Generate reports
    print("8. GENERATE REPORTS")
    print("-" * 80)

    # Text report
    print("TEXT REPORT (excerpt):")
    text_report = skill.generate_report(sample_code, format="text")
    lines = text_report.split("\n")[:20]
    print("\n".join(lines))
    print("... (truncated)")
    print()

    # JSON report
    print("JSON REPORT (excerpt):")
    import json
    json_report = skill.generate_report(sample_code, format="json")
    data = json.loads(json_report)
    print(f"  file_path: {data['file_path']}")
    print(f"  quality_score: {data['quality_score']}")
    print(f"  total_issues: {data['total_issues']}")
    print(f"  patterns_detected: {data['patterns_detected']}")
    print()

    # Markdown report
    print("MARKDOWN REPORT (excerpt):")
    md_report = skill.generate_report(sample_code, format="markdown")
    lines = md_report.split("\n")[:15]
    print("\n".join(lines))
    print("... (truncated)")
    print()

    print("=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
