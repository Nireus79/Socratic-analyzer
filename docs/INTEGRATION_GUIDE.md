# Socratic Analyzer - Integration Guide

## Socrates Nexus Integration

Use LLM for intelligent recommendations:

```python
from socratic_analyzer.llm import LLMPoweredAnalyzer
from socrates_nexus import LLMClient

analyzer = AnalyzerClient()
llm = LLMClient(provider="anthropic", model="claude-opus")

llm_analyzer = LLMPoweredAnalyzer(analyzer, llm)
result = llm_analyzer.analyze_with_insights("code.py")
```

## Openclaw Integration

```python
from socratic_analyzer.integrations.openclaw import AnalyzerSkill

skill = AnalyzerSkill(detailed=True)
result = skill.analyze("mycode.py")
```

## LangChain Integration

```python
from socratic_analyzer.integrations.langchain import SocraticAnalyzerTool

tool = SocraticAnalyzerTool()
# Use in LangChain agent
```

## CI/CD Integration

```bash
# Pre-commit hook
socratic-analyzer --check ./src --fail-on-critical

# GitHub Actions
- name: Analyze Code
  run: socratic-analyzer ./src --report json --output analysis.json
```
