# Socratic Analyzer - Troubleshooting

## Analysis Issues

### No issues detected

Possible cause: Code is clean or analysis disabled

Solution: Check configuration
```python
config = AnalyzerConfig(
    analyze_security=True,  # Must be True
    analyze_performance=True
)
```

### Slow analysis

Cause: Large files or projects

Solution: Analyze specific files
```python
# Instead of whole project
analyzer.analyze_file("specific_file.py")
```

## LLM Integration Issues

### LLM insights not available

Cause: LLM client not configured

Solution: Pass LLM client:
```python
llm = LLMClient(provider="anthropic")
llm_analyzer = LLMPoweredAnalyzer(analyzer, llm)
```

### Expensive LLM calls

Solution: Use cheaper model:
```python
llm = LLMClient(provider="openai", model="gpt-3.5-turbo")
```

## Report Issues

### Report format invalid

Solution: Use valid format
```python
report = analyzer.generate_report(analysis, format="json")
# Valid: "text", "json", "markdown"
```
