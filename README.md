# Socratic Analyzer

Production-grade code analysis package with LLM-powered insights. Analyze Python code for issues, metrics, patterns, and get intelligent recommendations.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI Status](https://img.shields.io/badge/PyPI-Coming%20Soon-blue.svg)](https://pypi.org/)

## Overview

Socratic Analyzer provides automated code analysis with static analysis, complexity metrics, pattern detection, and LLM-powered recommendations. Perfect for code quality assurance, refactoring guidance, and architectural insights.

### Key Features

- **Static Code Analysis** - Detect issues, violations, and code smells
- **Complexity Metrics** - Calculate cyclomatic complexity, maintainability index, and more
- **Pattern Detection** - Identify antipatterns, design patterns, and performance issues
- **Security Analysis** - Find potential security vulnerabilities
- **Documentation Analysis** - Check docstrings and type hints
- **Project-Wide Analysis** - Aggregate metrics across entire projects
- **Quality Scoring** - Get overall code quality score (0-100)
- **LLM Integration** - Get intelligent recommendations via Socrates Nexus
- **Multiple Formats** - Generate reports in text, JSON, and Markdown
- **Framework Integration** - Use as Openclaw skill or LangChain tool

## Installation

```bash
# Basic installation
pip install socratic-analyzer

# With Openclaw support
pip install socratic-analyzer[openclaw]

# With LangChain support
pip install socratic-analyzer[langchain]

# With all features
pip install socratic-analyzer[all]

# Development
pip install socratic-analyzer[dev]
```

## Quick Start

### Basic File Analysis

```python
from socratic_analyzer import AnalyzerClient, AnalyzerConfig

# Create analyzer
analyzer = AnalyzerClient(AnalyzerConfig())

# Analyze a file
analysis = analyzer.analyze_file("mycode.py")

# Print results
print(f"Issues: {analysis.total_issues}")
print(f"Patterns detected: {len(analysis.patterns)}")

# Generate report
report = analyzer.generate_report(analysis, format="text")
print(report)
```

### Project Analysis

```python
from socratic_analyzer import AnalyzerClient

analyzer = AnalyzerClient()

# Analyze entire project
project_analysis = analyzer.analyze_project("./src")

print(f"Files analyzed: {project_analysis.files_analyzed}")
print(f"Total issues: {project_analysis.total_issues}")
print(f"Quality score: {project_analysis.overall_score:.1f}/100")

# Get recommendations
for recommendation in project_analysis.recommendations:
    print(f"- {recommendation}")
```

### LLM-Powered Analysis

```python
from socratic_analyzer import AnalyzerClient
from socratic_analyzer.llm import LLMPoweredAnalyzer
from socrates_nexus import LLMClient

# Create components
analyzer = AnalyzerClient()
llm_client = LLMClient(provider="anthropic", model="claude-opus")

# Create LLM-powered analyzer
llm_analyzer = LLMPoweredAnalyzer(analyzer, llm_client)

# Get analysis with intelligent insights
result = llm_analyzer.analyze_with_insights("complex_module.py")
print(result["llm_insights"])
```

### Openclaw Integration

```python
from socratic_analyzer.integrations.openclaw import AnalyzerSkill

# Use in Openclaw
skill = AnalyzerSkill(detailed=True)
result = skill.analyze("mycode.py")
```

### LangChain Integration

```python
from socratic_analyzer.integrations.langchain import SocraticAnalyzerTool
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.llms import OpenAI

# Create tool
analyzer_tool = SocraticAnalyzerTool()

# Use in LangChain agent
tools = [
    Tool(
        name="analyze_code",
        func=analyzer_tool._run,
        description="Analyze Python code for issues and patterns"
    )
]

agent = initialize_agent(
    tools,
    OpenAI(temperature=0),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
```

## Architecture

### Core Components

**Analyzers** - Pluggable analysis strategies:
- StaticAnalyzer - Code issues and violations
- ComplexityAnalyzer - Cyclomatic complexity
- MetricsAnalyzer - Code metrics
- DocstringAnalyzer - Documentation quality
- TypeHintAnalyzer - Type hint completeness
- SecurityAnalyzer - Security issues

**Patterns** - Pattern detection:
- AntipatternDetector - Common antipatterns
- DesignPatternDetector - Design patterns
- PerformancePatternDetector - Performance issues

**Reports** - Output formats:
- TextReportFormatter
- JSONReportFormatter
- MarkdownReportFormatter

**Insights** - Intelligence generation:
- Scoring system (0-100 quality score)
- Recommendation generator
- LLM integration for intelligent insights

## Configuration

```python
from socratic_analyzer import AnalyzerConfig, AnalyzerClient

config = AnalyzerConfig(
    # Analysis options
    analyze_types=True,           # Check type hints
    analyze_docstrings=True,      # Check documentation
    analyze_security=True,        # Check security issues
    analyze_performance=True,     # Check performance antipatterns

    # Thresholds
    max_complexity=10,            # Max cyclomatic complexity
    max_line_length=120,          # Max line length
    min_docstring_length=10,      # Min docstring length

    # Output
    include_metrics=True,
    include_patterns=True,
    detailed_output=False,

    # LLM Integration
    use_llm=True,
    llm_provider="anthropic",
    llm_model="claude-opus",
)

analyzer = AnalyzerClient(config)
```

## Output Formats

### Text Report

```
=== Analysis Report: example.py ===

FILE INFORMATION
  Size: 2,048 bytes
  Lines: 45

ISSUES (5 total)
  CRITICAL: example.py:12 - Function 'process_data' is too complex (CC: 15)
    Suggestion: Refactor into smaller functions

  HIGH: example.py:25 - Unused variable 'temp_result'

  MEDIUM: example.py:8 - Missing type hints

METRICS
  Cyclomatic Complexity: 15 (threshold: 10)
  Maintainability Index: 62.5

PATTERNS DETECTED
  - Unused variable pattern
  - Long function pattern
```

### JSON Report

```json
{
  "file_path": "example.py",
  "total_issues": 5,
  "critical_issues": 1,
  "issues": [
    {
      "type": "complexity",
      "severity": "critical",
      "location": "example.py:12",
      "message": "Function too complex",
      "suggestion": "Refactor..."
    }
  ],
  "metrics": [...],
  "overall_score": 62.5
}
```

### Markdown Report

```markdown
# Analysis Report: example.py

## Summary
- **Files analyzed**: 1
- **Issues**: 5 (1 critical, 1 high, 3 medium)
- **Quality score**: 62.5/100

## Critical Issues
1. **Function 'process_data' too complex** (CC: 15)
   - Location: `example.py:12`
   - Suggestion: Refactor into smaller functions

## Recommendations
- Fix critical issues immediately
- Address high-severity issues
```

## Examples

See the `examples/` directory for complete working examples:

- `01_basic_analysis.py` - Analyze a single file
- `02_pattern_detection.py` - Detect code patterns
- `03_scoring_analysis.py` - Get quality scores
- `04_project_analysis.py` - Analyze entire projects
- `05_openclaw_integration.py` - Use as Openclaw skill
- `06_langchain_integration.py` - Use in LangChain agents
- `07_llm_powered_analysis.py` - Get LLM insights

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/socratic_analyzer

# Run specific test
pytest tests/test_models.py::TestAnalyzerConfig

# Run benchmarks
pytest tests/benchmarks/ -v
```

## API Reference

### AnalyzerClient

Main interface for code analysis.

```python
class AnalyzerClient:
    def analyze_file(self, file_path: str) -> Analysis
    def analyze_project(self, project_path: str) -> ProjectAnalysis
    def generate_report(self, analysis, format: str) -> str
```

### Analysis Model

```python
@dataclass
class Analysis:
    file_path: str
    file_size: int
    language: str
    issues: List[CodeIssue]
    metrics: List[MetricResult]
    patterns: List[str]
    timestamp: datetime
```

### CodeIssue Model

```python
@dataclass
class CodeIssue:
    issue_type: str        # "complexity", "style", "security", etc.
    severity: str          # "critical", "high", "medium", "low", "info"
    location: str          # "file.py:123"
    message: str
    suggestion: Optional[str]
```

## Performance

Based on benchmarks:

- **Single file** (1-5 KB): ~10-50ms
- **Medium file** (50 KB): ~100-200ms
- **Large file** (500 KB): ~500ms-1s
- **Batch operation**: 10-15ms per file

## Integration with Socrates Ecosystem

Socratic Analyzer integrates seamlessly with:

- **Socrates Nexus** - Multi-provider LLM client for intelligent recommendations
- **Openclaw** - Available as reusable skill
- **LangChain** - Available as tool for agents

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- GitHub Issues: https://github.com/Nireus79/Socratic-analyzer/issues
- Documentation: https://github.com/Nireus79/Socratic-analyzer/tree/main/docs
- Email: info@socratic-analyzer.dev

---

**Built with ❤️ as part of the Socrates ecosystem**

Made by [@Nireus79](https://github.com/Nireus79)
