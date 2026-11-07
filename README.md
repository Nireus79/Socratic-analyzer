> **Proof of concept, not a product.** This library belongs to the earlier Python research prototype ([Socrates](https://github.com/Nireus79/Socrates)) and is not maintained as a product. The current products are listed at [nireus79.github.io](https://nireus79.github.io/). Contact: Hermes_creative@proton.me.

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
- `analytics_calculator.AnalyticsCalculator` - Calculate metrics from project data
- `maturity_calculator.MaturityCalculator` - Assess project maturity
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

### Cost of a workflow path

```python
from socratic_analyzer.core import WorkflowCostCalculator
from socratic_analyzer.models import (
    WorkflowDefinition, WorkflowEdge, WorkflowNode, WorkflowPath,
)
from socratic_analyzer.models.workflow import WorkflowNodeType

workflow = WorkflowDefinition(
    workflow_id="wf-1",
    name="Analysis workflow",
    phase="analysis",
    nodes={
        "start": WorkflowNode("start", WorkflowNodeType.PHASE_START, "Start"),
        "review": WorkflowNode("review", WorkflowNodeType.ANALYSIS, "Review", estimated_tokens=500),
        "end": WorkflowNode("end", WorkflowNodeType.PHASE_END, "End"),
    },
    edges=[
        WorkflowEdge(from_node="start", to_node="review", cost=10),
        WorkflowEdge(from_node="review", to_node="end", cost=5),
    ],
    start_node="start",
    end_nodes=["end"],
)
path = WorkflowPath(path_id="p1", nodes=["start", "review", "end"], edges=[])

print(WorkflowCostCalculator().calculate_path_cost(path, workflow))
# {'total_tokens': 500, 'total_cost_usd': 0.0225, 'token_breakdown': {...}}
```

### Validate dependencies

```python
from socratic_analyzer.utils.validators import DependencyValidator

result = DependencyValidator().validate("./requirements.txt")
print(result["valid"], result["issues"], result["warnings"])
```

`validate` takes a project directory or a file and returns a dict with `valid`, `issues`, `warnings` and `metadata`.

### Phase maturity

```python
from socratic_analyzer.maturity_calculator import MaturityCalculator

calculator = MaturityCalculator()
print(calculator.get_phase_categories("discovery"))  # category -> target points

specs = [{"category": "problem_definition", "confidence": 0.9, "value": 1.0}]
maturity = calculator.calculate_phase_maturity(specs, "discovery")
print(maturity.overall_score, maturity.missing_categories)
```

The phases are discovery, analysis, design and implementation; the score is the confidence-weighted sum per category, capped at the category target, as a percentage of 90.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/socratic_analyzer

# Run specific tests
pytest tests/test_module_imports.py -v
```

## Code Quality

All checks passing:
- ✅ Black formatting
- ✅ Ruff linting
- ✅ Mypy type checking (pragmatic for extracted library)

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


---

## Origin

This package comes from the [Socrates](https://github.com/Nireus79/Socrates) research prototype, which is not maintained as a product. Status: alpha. Written by Efthimios Angelopoulos with AI coding assistants (Claude Code); I design, review and test it. Contact: Hermes_creative@proton.me.

### Use This Package Standalone:
```bash
pip install socratic-analyzer
```

### Or As Part of Socrates Platform:
```bash
pip install socrates-ai  # the earlier research prototype that uses this package
```

### More Information:
- 📖 [Full Socrates Documentation](https://github.com/Nireus79/Socrates/tree/main/docs)
- 💬 [Socrates Discussions](https://github.com/Nireus79/Socrates/discussions)

---
