# Socratic Analyzer - API Reference

## AnalyzerClient

### analyze_file(file_path) -> Analysis
Analyze single Python file.

### analyze_project(project_path) -> ProjectAnalysis
Analyze all Python files in directory.

### generate_report(analysis, format="text") -> str
Generate formatted report.

Formats: "text", "json", "markdown"

## AnalyzerConfig

Configuration options:
```python
AnalyzerConfig(
    analyze_types=True,
    analyze_docstrings=True,
    analyze_security=True,
    analyze_performance=True,
    max_complexity=10,
    max_line_length=120,
    min_docstring_length=10
)
```

## Analysis Model

```python
@dataclass
class Analysis:
    file_path: str
    total_issues: int
    issues: List[CodeIssue]
    metrics: List[MetricResult]
    patterns: List[str]
```

## CodeIssue

```python
@dataclass
class CodeIssue:
    issue_type: str
    severity: str  # critical, high, medium, low
    location: str  # file:line
    message: str
    suggestion: Optional[str]
```
