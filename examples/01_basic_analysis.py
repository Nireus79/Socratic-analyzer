"""
Basic workflow analysis example.

Demonstrates how to create a workflow, analyze its cost, and find optimal paths.
"""

from datetime import datetime

from socratic_analyzer.models import (
    ProjectContext,
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowNode,
)
from socratic_analyzer.core import (
    WorkflowCostCalculator,
    WorkflowPathFinder,
    WorkflowRiskCalculator,
)


def main() -> None:
    """Run basic workflow analysis example."""
    print("=" * 80)
    print("SOCRATIC ANALYZER - WORKFLOW ANALYSIS EXAMPLE")
    print("=" * 80)
    print()

    # Create a sample workflow definition
    workflow = WorkflowDefinition(
        workflow_id="wf-001",
        name="Development Workflow",
        description="Standard development process workflow",
        nodes=[
            WorkflowNode(id="start", name="Start", node_type="start"),
            WorkflowNode(id="analysis", name="Analysis", node_type="process"),
            WorkflowNode(id="design", name="Design", node_type="process"),
            WorkflowNode(id="implementation", name="Implementation", node_type="process"),
            WorkflowNode(id="testing", name="Testing", node_type="process"),
            WorkflowNode(id="review", name="Code Review", node_type="process"),
            WorkflowNode(id="end", name="End", node_type="end"),
        ],
        edges=[
            WorkflowEdge(source="start", target="analysis", cost=5),
            WorkflowEdge(source="analysis", target="design", cost=10),
            WorkflowEdge(source="design", target="implementation", cost=20),
            WorkflowEdge(source="implementation", target="testing", cost=15),
            WorkflowEdge(source="testing", target="review", cost=8),
            WorkflowEdge(source="review", target="end", cost=2),
            # Alternative path: fast-track from analysis to implementation
            WorkflowEdge(source="analysis", target="implementation", cost=15),
        ],
    )

    # Create project context
    project = ProjectContext(
        project_id="proj-001",
        name="Sample Project",
        owner="developer@example.com",
        phase="implementation",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        workflow=workflow,
    )

    print("PROJECT INFORMATION")
    print("-" * 80)
    print(f"Project: {project.name}")
    print(f"Owner: {project.owner}")
    print(f"Phase: {project.phase}")
    print(f"Workflow: {workflow.name}")
    print(f"Nodes: {len(workflow.nodes)}")
    print(f"Edges: {len(workflow.edges)}")
    print()

    # Analyze workflow costs
    print("WORKFLOW COST ANALYSIS")
    print("-" * 80)
    cost_calculator = WorkflowCostCalculator()
    total_cost = cost_calculator.calculate_workflow_costs(project)
    print(f"Total workflow cost: {total_cost}")
    print()

    # Find optimal paths
    print("WORKFLOW PATHS")
    print("-" * 80)
    path_finder = WorkflowPathFinder()
    paths = path_finder.find_workflow_paths(project)
    for i, path in enumerate(paths[:3], 1):  # Show top 3 paths
        print(f"Path {i}: {' → '.join([node.name for node in path.nodes])}")
        print(f"  Cost: {path.cost}")
        print()

    # Analyze workflow risks
    print("WORKFLOW RISK ANALYSIS")
    print("-" * 80)
    risk_calculator = WorkflowRiskCalculator()
    risks = risk_calculator.calculate_workflow_risks(project)
    print(f"Total risk score: {risks.overall_risk_score}")
    print(f"Risk level: {risks.risk_level}")
    print()

    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
