# Socratic Analyzer - Guides by Role

## For Developers

Extend analysis by:
- Creating custom analyzer (inherit from BaseAnalyzer)
- Adding pattern detectors
- Creating custom report formatters

Use for:
- Code review automation
- Quality gates in CI/CD
- Refactoring guidance

## For DevOps

Deploy for:
- Pre-commit hooks (fast analysis)
- CI/CD pipeline gates (block low quality)
- Nightly batch analysis (comprehensive)

Configuration:
```python
config = AnalyzerConfig(
    analyze_security=True,
    max_complexity=10,
    include_metrics=True
)
```

## For Data Scientists

Use to:
- Analyze code quality of experiments
- Track code metrics over time
- Compare code approaches

## For Business Users

Benefits:
- Catch issues before production
- Improve code maintainability
- Ensure consistent quality
- Reduce technical debt
