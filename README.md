# Socratic Analyzer

**Status**: Independent library extracted from Socrates monolith (v0.1.5)

Code analysis and workflow optimization library for project development, quality assessment, and architectural insights. Part of the Socratic Ecosystem.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Black-passing-brightgreen.svg)](https://github.com/psf/black)

## Overview

Socratic Analyzer provides tools for analyzing project workflows, assessing code complexity, tracking maturity, and identifying optimization opportunities.

### Key Capabilities

- **Workflow Analysis** - Analyze project workflows and process paths
- **Complexity Metrics** - Calculate workflow costs and identify bottlenecks
- **Code Validation** - Validate dependencies, syntax, and test execution
- **Project Context** - Model projects with phases, team structure, and maturity tracking
- **Quality Assessment** - Track project maturity across phases and categories
- **Insight Categorization** - Categorize insights and recommendations by workflow phase

## Architecture

### Core Modules

**Workflow Analysis**:
- `WorkflowCostCalculator` - Calculate execution costs of workflow paths
- `WorkflowPathFinder` - Discover optimal workflow paths
- `WorkflowRiskCalculator` - Assess risks in workflow execution

**Code Quality**:
- `InsightCategorizer` - Categorize insights by phase and workflow
- `DependencyValidator` - Validate project dependencies
- `SyntaxValidator` - Validate code syntax
- `TestExecutor` - Execute and track test results

**Data Models**:
- `ProjectContext` - Complete project information and state
- `TeamMemberRole` - Team member roles and skills
- `WorkflowDefinition` - Workflow paths and execution states

**Analytics**:
- `AnalyticsCalculator` - Calculate metrics from project data
- `MaturityCalculator` - Assess project maturity
- `TokenUsage` - Track LLM usage and costs

## Installation

```bash
# Basic installation
pip install socratic-analyzer

# With framework integrations
pip install socratic-analyzer[langchain]
pip install socratic-analyzer[nexus]

# Development
pip install socratic-analyzer[dev]
```

### Dependencies

**Core**:
- `socratic-maturity>=0.1.1` - Maturity tracking and assessment
- `socratic-nexus>=0.3.6` - Multi-provider LLM integration

**Optional**:
- `langchain>=0.1.0` - LangChain integration
- `langgraph>=0.0.1` - Graph-based workflows

## Quick Start

### Analyze a Project

```python
from socratic_analyzer.models import ProjectContext
from socratic_analyzer.core import WorkflowCostCalculator

# Create project context
project = ProjectContext(
    project_id="proj-123",
    name="MyProject",
    owner="user@example.com",
    phase="analysis",
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Analyze workflow costs
calculator = WorkflowCostCalculator()
costs = calculator.calculate_workflow_costs(project)
print(f"Estimated cost: {costs}")
```

### Validate Code Dependencies

```python
from socratic_analyzer.utils.validators import DependencyValidator

validator = DependencyValidator()

# Check dependency compatibility
issues = validator.validate_dependencies("./requirements.txt")
for issue in issues:
    print(f"Issue: {issue['type']} - {issue['message']}")
```

### Track Project Maturity

```python
from socratic_analyzer.maturity_calculator import MaturityCalculator

calculator = MaturityCalculator()

# Calculate overall maturity
maturity = calculator.calculate_maturity(project)
print(f"Project maturity: {maturity.overall_score}%")
print(f"Phase scores: {maturity.phase_maturity_scores}")
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/socratic_analyzer

# Run specific tests
pytest tests/test_module_imports.py -v
```

**Current Coverage**: 15.76% (import verification tests)
**Required Threshold**: 5% ✅

## Code Quality

All checks passing:
- ✅ Black formatting
- ✅ Ruff linting
- ✅ Mypy type checking (pragmatic for extracted library)

## Configuration Examples

### Workflow Analysis

```python
from socratic_analyzer.models import WorkflowDefinition, WorkflowNode, WorkflowEdge

# Define workflow
workflow = WorkflowDefinition(
    workflow_id="wf-123",
    name="Analysis Workflow",
    description="Project analysis process",
    nodes=[
        WorkflowNode(id="start", name="Start", node_type="start"),
        WorkflowNode(id="analysis", name="Analysis", node_type="process"),
        WorkflowNode(id="review", name="Review", node_type="process"),
        WorkflowNode(id="end", name="End", node_type="end"),
    ],
    edges=[
        WorkflowEdge(source="start", target="analysis", cost=10),
        WorkflowEdge(source="analysis", target="review", cost=15),
        WorkflowEdge(source="review", target="end", cost=5),
    ]
)
```

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and component overview
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation (when available)
- **[Integration Guide](docs/INTEGRATION_GUIDE.md)** - How to integrate with other systems

## Part of the Socratic Ecosystem

Socratic Analyzer integrates with:

- **[Socratic Nexus](https://github.com/Nireus79/Socrates-nexus)** - Multi-provider LLM client
- **[Socratic Maturity](https://github.com/Nireus79/Socratic-maturity)** - Maturity tracking (dependency)
- **[Socratic Agents](https://github.com/Nireus79/Socratic-agents)** - Agent orchestration (optional)
- **[Socratic Learning](https://github.com/Nireus79/Socratic-learning)** - Learning patterns (optional)

See [Socratic Ecosystem](https://github.com/Nireus79/Socrates-nexus/blob/main/ECOSYSTEM.md) for complete overview.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- **Issues**: https://github.com/Nireus79/Socratic-analyzer/issues
- **Documentation**: https://github.com/Nireus79/Socratic-analyzer/tree/main/docs

---

**Built as part of the Socratic ecosystem**

Made by [@Nireus79](https://github.com/Nireus79)
