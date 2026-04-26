"""
Project maturity analysis example.

Demonstrates how to assess project maturity and categorize insights.
"""

from datetime import datetime, timedelta

from socratic_analyzer.models import ProjectContext, CategoryScore, PhaseMaturity
from socratic_analyzer.core import InsightCategorizer


def main() -> None:
    """Run project maturity analysis example."""
    print("=" * 80)
    print("SOCRATIC ANALYZER - PROJECT MATURITY ANALYSIS EXAMPLE")
    print("=" * 80)
    print()

    # Create a project context with maturity information
    project = ProjectContext(
        project_id="proj-maturity-001",
        name="Mature Development Project",
        owner="team@example.com",
        phase="implementation",
        created_at=datetime.now() - timedelta(days=365),  # 1 year old
        updated_at=datetime.now(),
    )

    # Set maturity scores for different categories
    project.maturity = PhaseMaturity(
        phase="implementation",
        timestamp=datetime.now(),
        category_scores={
            "code_quality": CategoryScore(
                category="code_quality",
                score=75,
                max_score=100,
                description="Well-maintained code with good structure",
            ),
            "testing": CategoryScore(
                category="testing",
                score=68,
                max_score=100,
                description="Comprehensive test coverage but some edge cases missing",
            ),
            "documentation": CategoryScore(
                category="documentation",
                score=82,
                max_score=100,
                description="Well-documented API and architecture",
            ),
            "security": CategoryScore(
                category="security",
                score=70,
                max_score=100,
                description="Good security practices but some hardening needed",
            ),
        },
    )

    print("PROJECT INFORMATION")
    print("-" * 80)
    print(f"Project: {project.name}")
    print(f"Owner: {project.owner}")
    print(f"Phase: {project.phase}")
    print(f"Age: {(datetime.now() - project.created_at).days} days")
    print()

    print("MATURITY SCORES")
    print("-" * 80)
    if project.maturity and project.maturity.category_scores:
        overall_score = sum(
            cat.score for cat in project.maturity.category_scores.values()
        ) / len(project.maturity.category_scores)
        print(f"Overall Maturity: {overall_score:.1f}/100")
        print()

        for category_name, score in project.maturity.category_scores.items():
            percentage = (score.score / score.max_score) * 100
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            print(f"  {category_name:15} [{bar}] {score.score}/{score.max_score}")
            if score.description:
                print(f"                  {score.description}")
        print()

    # Categorize sample insights
    print("INSIGHT CATEGORIZATION")
    print("-" * 80)

    insights = [
        "Code has too many long methods that should be refactored",
        "Test coverage is below 80% in critical modules",
        "API documentation is missing endpoint examples",
        "SQL injection vulnerability found in user input handling",
        "Performance bottleneck detected in database queries",
        "Team should establish CI/CD best practices",
    ]

    categorizer = InsightCategorizer()
    categorized = categorizer.categorize_insights(insights, project)

    if categorized:
        print(f"Categorized {len(insights)} insights by phase:")
        print()
        for phase, phase_insights in categorized.items():
            print(f"{phase.upper()}:")
            for insight in phase_insights:
                print(f"  • {insight}")
            print()
    else:
        print("No categorized insights available")

    print()

    print("RECOMMENDATIONS BY PHASE")
    print("-" * 80)

    phases = ["discovery", "analysis", "design", "implementation"]
    for phase in phases:
        recommendations = categorizer.get_phase_recommendations(project, phase)
        print(f"{phase.upper()}:")
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                print(f"  {i}. {rec}")
        else:
            print("  No specific recommendations for this phase")
        print()

    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
