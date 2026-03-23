# Socratic Analyzer

Production-grade code analysis with LLM-powered insights for the Socratic AI platform.

## Features

- **LLM-Powered Analysis**: Uses Claude AI for intelligent code review
- **Security Scanning**: Identifies security vulnerabilities and concerns
- **Performance Analysis**: Detects performance bottlenecks and inefficiencies
- **Quality Metrics**: Calculates code quality, complexity, and maintainability scores
- **Actionable Insights**: Generates prioritized, actionable recommendations
- **Batch Analysis**: Analyze multiple code snippets efficiently

## Installation

```bash
pip install socratic-analyzer
```

With LLM support:

```bash
pip install socratic-analyzer[anthropic]
```

## Quick Start

```python
from socratic_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# Analyze code
result = analyzer.analyze("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""", language="python")

print(result.issues)
print(result.recommendations)
```

## Components

### CodeAnalyzer

Main analyzer class providing code analysis functionality.

```python
analyzer = CodeAnalyzer()
result = analyzer.analyze(code, language="python")
```

### InsightGenerator

Transforms analysis results into actionable insights.

```python
from socratic_analyzer import InsightGenerator

generator = InsightGenerator()
insights = generator.generate_insights(analysis_data)
prioritized = generator.prioritize_insights(insights)
```

### QualityMetrics

Calculates code quality metrics.

```python
from socratic_analyzer import QualityMetrics
from socratic_analyzer.metrics import MetricsCalculator

metrics = MetricsCalculator.calculate_metrics(code)
print(metrics.overall_quality)
```

## Configuration

Set `ANTHROPIC_API_KEY` environment variable to enable LLM analysis.

## License

MIT
