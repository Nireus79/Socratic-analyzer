# Socratic Analyzer - FAQ by Scenario

## Scenario 1: Basic File Analysis

How do I analyze a single Python file?

```python
from socratic_analyzer import AnalyzerClient

analyzer = AnalyzerClient()
analysis = analyzer.analyze_file("mycode.py")

print(f"Issues: {analysis.total_issues}")
print(f"Complexity: {[m for m in analysis.metrics if m.name=='cyclomatic_complexity']}")
```

## Scenario 2: Project Analysis

How do I analyze an entire project?

```python
project_analysis = analyzer.analyze_project("./src")
print(f"Files: {project_analysis.files_analyzed}")
print(f"Quality score: {project_analysis.overall_score:.1f}/100")
```

## Scenario 3: LLM-Powered Insights

How do I get AI recommendations?

```python
from socratic_analyzer.llm import LLMPoweredAnalyzer
from socrates_nexus import LLMClient

llm_client = LLMClient(provider="anthropic")
llm_analyzer = LLMPoweredAnalyzer(analyzer, llm_client)

result = llm_analyzer.analyze_with_insights("code.py")
print(result["llm_insights"])
```

## Scenario 4: Report Generation

How do I generate reports?

```python
analysis = analyzer.analyze_file("code.py")

# Text report
text = analyzer.generate_report(analysis, format="text")

# JSON report
json_report = analyzer.generate_report(analysis, format="json")

# Markdown report
md_report = analyzer.generate_report(analysis, format="markdown")
```

## Scenario 5: Custom Configuration

How do I customize analysis?

```python
from socratic_analyzer import AnalyzerConfig

config = AnalyzerConfig(
    analyze_security=True,
    max_complexity=8,
    max_line_length=100,
    min_docstring_length=20
)

analyzer = AnalyzerClient(config)
```
