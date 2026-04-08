"""Tests for insight generation module."""

import pytest

from socratic_analyzer.insights import InsightData, InsightGenerator


class TestInsightData:
    """Test InsightData model."""

    def test_insight_data_creation(self):
        """Test creating insight data with all fields."""
        insight = InsightData(
            category="code_quality",
            title="Test Issue",
            description="A test issue description",
            severity="warning",
            actionable=True,
        )

        assert insight.category == "code_quality"
        assert insight.title == "Test Issue"
        assert insight.description == "A test issue description"
        assert insight.severity == "warning"
        assert insight.actionable is True

    def test_insight_data_defaults(self):
        """Test InsightData defaults."""
        insight = InsightData(
            category="performance",
            title="Performance Issue",
            description="Description",
        )

        assert insight.severity == "info"
        assert insight.actionable is True

    def test_insight_data_validation(self):
        """Test InsightData field validation."""
        # Missing required fields should fail
        with pytest.raises(ValueError):
            InsightData(category="test")  # Missing title and description


class TestInsightGenerator:
    """Test InsightGenerator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = InsightGenerator()

        assert len(generator.categories) == 6
        assert "code_quality" in generator.categories
        assert "performance" in generator.categories
        assert "security" in generator.categories
        assert "maintainability" in generator.categories
        assert "testing" in generator.categories
        assert "documentation" in generator.categories

    def test_generate_insights_from_issues(self):
        """Test generating insights from issues."""
        generator = InsightGenerator()

        analysis_data = {
            "issues": ["Issue 1", "Issue 2"],
            "improvements": [],
            "security_concerns": [],
            "performance_concerns": [],
        }

        insights = generator.generate_insights(analysis_data)

        assert len(insights) == 2
        assert all(i.category == "code_quality" for i in insights)
        assert all(i.severity == "warning" for i in insights)
        assert insights[0].description == "Issue 1"
        assert insights[1].description == "Issue 2"

    def test_generate_insights_from_improvements(self):
        """Test generating insights from improvements."""
        generator = InsightGenerator()

        analysis_data = {
            "issues": [],
            "improvements": ["Improve 1", "Improve 2"],
            "security_concerns": [],
            "performance_concerns": [],
        }

        insights = generator.generate_insights(analysis_data)

        assert len(insights) == 2
        assert all(i.category == "maintainability" for i in insights)
        assert all(i.severity == "info" for i in insights)

    def test_generate_insights_from_security_concerns(self):
        """Test generating insights from security concerns."""
        generator = InsightGenerator()

        analysis_data = {
            "issues": [],
            "improvements": [],
            "security_concerns": ["SQL injection vulnerability"],
            "performance_concerns": [],
        }

        insights = generator.generate_insights(analysis_data)

        assert len(insights) == 1
        assert insights[0].category == "security"
        assert insights[0].severity == "critical"

    def test_generate_insights_from_performance_concerns(self):
        """Test generating insights from performance concerns."""
        generator = InsightGenerator()

        analysis_data = {
            "issues": [],
            "improvements": [],
            "security_concerns": [],
            "performance_concerns": ["Loop inefficiency"],
        }

        insights = generator.generate_insights(analysis_data)

        assert len(insights) == 1
        assert insights[0].category == "performance"
        assert insights[0].severity == "warning"

    def test_generate_insights_mixed(self):
        """Test generating insights from multiple categories."""
        generator = InsightGenerator()

        analysis_data = {
            "issues": ["Issue 1"],
            "improvements": ["Improve 1"],
            "security_concerns": ["Security issue"],
            "performance_concerns": ["Performance issue"],
        }

        insights = generator.generate_insights(analysis_data)

        assert len(insights) == 4
        categories = {i.category for i in insights}
        assert categories == {
            "code_quality",
            "maintainability",
            "security",
            "performance",
        }

    def test_generate_insights_empty_data(self):
        """Test generating insights from empty analysis data."""
        generator = InsightGenerator()

        analysis_data = {
            "issues": [],
            "improvements": [],
            "security_concerns": [],
            "performance_concerns": [],
        }

        insights = generator.generate_insights(analysis_data)

        assert len(insights) == 0

    def test_prioritize_insights(self):
        """Test prioritizing insights by severity."""
        generator = InsightGenerator()

        insights = [
            InsightData(
                category="code_quality",
                title="Minor",
                description="Info",
                severity="info",
            ),
            InsightData(
                category="security",
                title="Critical",
                description="Security",
                severity="critical",
            ),
            InsightData(
                category="performance",
                title="Warning",
                description="Performance",
                severity="warning",
            ),
        ]

        prioritized = generator.prioritize_insights(insights)

        # Check that critical comes first
        assert prioritized[0].severity == "critical"
        assert prioritized[1].severity == "warning"
        assert prioritized[2].severity == "info"

    def test_prioritize_insights_actionable(self):
        """Test that actionable insights are prioritized within same severity."""
        generator = InsightGenerator()

        insights = [
            InsightData(
                category="code_quality",
                title="Not actionable",
                description="Desc",
                severity="warning",
                actionable=False,
            ),
            InsightData(
                category="code_quality",
                title="Actionable",
                description="Desc",
                severity="warning",
                actionable=True,
            ),
        ]

        prioritized = generator.prioritize_insights(insights)

        # Actionable should come first
        assert prioritized[0].actionable is True
        assert prioritized[1].actionable is False

    def test_summarize_insights(self):
        """Test summarizing insights by category."""
        generator = InsightGenerator()

        insights = [
            InsightData(
                category="code_quality", title="1", description="D", severity="info"
            ),
            InsightData(
                category="code_quality", title="2", description="D", severity="info"
            ),
            InsightData(
                category="security", title="3", description="D", severity="critical"
            ),
            InsightData(
                category="performance", title="4", description="D", severity="warning"
            ),
        ]

        summary = generator.summarize_insights(insights)

        assert summary["code_quality"] == 2
        assert summary["security"] == 1
        assert summary["performance"] == 1
        assert summary["maintainability"] == 0
        assert summary["testing"] == 0
        assert summary["documentation"] == 0

    def test_summarize_insights_empty(self):
        """Test summarizing empty insights list."""
        generator = InsightGenerator()

        summary = generator.summarize_insights([])

        assert all(count == 0 for count in summary.values())
        assert len(summary) == 6
