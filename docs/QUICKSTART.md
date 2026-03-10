# Socratic Analyzer - Quick Start Guide

Get started with Socratic Analyzer in 5 minutes.

## Installation

```bash
pip install socratic-analyzer
```

## Basic Usage

### 1. Analyze a Single File

```python
from socratic_analyzer import AnalyzerClient

# Create analyzer
analyzer = AnalyzerClient()

# Analyze a file
analysis = analyzer.analyze_file("mycode.py")

# Print summary
print(f"Quality Score: {analysis.quality_score}/100")
print(f"Total Issues: {analysis.total_issues}")
print(f"Critical Issues: {analysis.critical_issues}")
```

### 2. Analyze Code String

```python
code = '''
def calculate(x, y):
    """Calculate sum."""
    return x + y
'''

analysis = analyzer.analyze_code(code, "example.py")

# Get recommendations
recommendations = analyzer.get_recommendations(analysis)
for rec in recommendations:
    print(f"- {rec}")
```

### 3. Generate Reports

```python
# Text report
text_report = analyzer.generate_report(analysis, format="text")
print(text_report)

# JSON report
json_report = analyzer.generate_report(analysis, format="json")

# Markdown report
md_report = analyzer.generate_report(analysis, format="markdown")
```

### 4. Access Analysis Details

```python
# Issues
for issue in analysis.issues:
    print(f"[{issue.severity}] {issue.message} at {issue.location}")
    if issue.suggestion:
        print(f"  Suggestion: {issue.suggestion}")

# Patterns
print(f"Patterns detected: {', '.join(analysis.patterns)}")

# Metrics
for metric in analysis.metrics:
    print(f"{metric.name}: {metric.value:.1f}")
```

## Using with Openclaw

```python
from socratic_analyzer.integrations.openclaw import SocraticAnalyzerSkill

# Create skill
skill = SocraticAnalyzerSkill()

# Use in Openclaw
result = skill.analyze_code(your_code)
print(f"Quality: {result['quality_score']}/100")

# Get recommendations
recommendations = skill.get_recommendations(your_code)
for rec in recommendations:
    print(f"- {rec}")
```

## Using with LangChain

```python
from socratic_analyzer.integrations.langchain import create_analyzer_tools
from langchain.agents import initialize_agent, AgentType

# Create tools
tools = create_analyzer_tools()

# Use in agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Run agent with your code
result = agent.run("Analyze this code and tell me the issues")
```

## Configuration

```python
from socratic_analyzer import AnalyzerClient, AnalyzerConfig

# Custom configuration
config = AnalyzerConfig(
    max_complexity=10,          # Max cyclomatic complexity
    include_metrics=True,       # Include metrics in analysis
    analyze_types=True,         # Analyze type hints
    analyze_docstrings=True,    # Check docstring coverage
    max_line_length=120,        # Max line length
)

# Create analyzer with config
analyzer = AnalyzerClient(config)
```

## What Gets Analyzed

### Static Analysis
- Unused variables
- Missing docstrings
- Type hint coverage
- Long lines
- Empty blocks
- Import organization

### Complexity Analysis
- Cyclomatic complexity
- Nesting depth
- Function length
- Class size

### Metrics
- Lines of code
- Maintainability index
- Function/method counts
- Class metrics

### Patterns
- Design patterns (Singleton, Factory, Decorator, etc.)
- Code smells (long methods, god classes, etc.)
- Performance issues (string concatenation in loops, etc.)

### Quality Scoring
- Overall quality score (0-100)
- Issue-based scoring
- Metrics-based scoring
- Quality ratings (Excellent to Critical)

## Examples

See the `examples/` directory for:
- `01_basic_analysis.py` - Basic analysis
- `02_batch_analysis.py` - Analyze multiple files
- `03_custom_config.py` - Custom configuration
- `05_openclaw_integration.py` - Openclaw usage
- `06_langchain_integration.py` - LangChain usage

## Next Steps

- Read [API Reference](API_REFERENCE.md) for detailed documentation
- Check [Integration Guide](INTEGRATIONS.md) for framework integration
- View [Examples](../examples/) for more use cases
- See [Contributing](CONTRIBUTING.md) to contribute
