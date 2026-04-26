"""
Basic import tests for module verification.

This test suite verifies that the socratic-analyzer module can be imported
and that its main components are available.
"""


def test_module_import():
    """Test that the module can be imported."""
    import socratic_analyzer

    assert socratic_analyzer is not None


def test_main_exports():
    """Test that main analysis classes are available."""
    from socratic_analyzer import (
        InsightCategorizer,
        WorkflowCostCalculator,
        WorkflowPathFinder,
        WorkflowRiskCalculator,
    )

    assert InsightCategorizer is not None
    assert WorkflowCostCalculator is not None
    assert WorkflowPathFinder is not None
    assert WorkflowRiskCalculator is not None


def test_data_models_available():
    """Test that data models can be imported."""
    from socratic_analyzer.models import (
        ProjectContext,
        TeamMemberRole,
        WorkflowDefinition,
    )

    assert ProjectContext is not None
    assert TeamMemberRole is not None
    assert WorkflowDefinition is not None


def test_utils_available():
    """Test that utility modules are available."""
    from socratic_analyzer.utils import DependencyValidator, SyntaxValidator

    assert DependencyValidator is not None
    assert SyntaxValidator is not None
