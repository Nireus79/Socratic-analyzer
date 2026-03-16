# Socratic Analyzer - Architecture & System Design

## System Overview

Socratic Analyzer provides code analysis with static analysis, complexity metrics, pattern detection, security analysis, and LLM-powered recommendations.

## Core Components

### 1. AnalyzerClient
Main interface for code analysis.

Methods:
- `analyze_file(path)` - Analyze single file
- `analyze_project(path)` - Analyze entire project
- `generate_report(analysis, format)` - Generate reports

### 2. Analyzers
Pluggable analysis strategies:
- StaticAnalyzer - Code issues/violations
- ComplexityAnalyzer - Cyclomatic complexity
- MetricsAnalyzer - Code metrics
- DocstringAnalyzer - Documentation quality
- TypeHintAnalyzer - Type hint completeness
- SecurityAnalyzer - Security vulnerabilities

### 3. Pattern Detection
- AntipatternDetector - Common antipatterns
- DesignPatternDetector - Design patterns
- PerformancePatternDetector - Performance issues

### 4. Report Formatters
- TextReportFormatter
- JSONReportFormatter
- MarkdownReportFormatter

### 5. Insights & Scoring
- Scoring system (0-100)
- Recommendation generator
- LLM integration for intelligent insights

## Data Models

### Analysis
Results of analyzing single file:
- file_path, file_size, language
- issues, metrics, patterns, timestamp

### CodeIssue
Single issue found:
- issue_type, severity, location, message, suggestion

### ProjectAnalysis
Aggregate results:
- files_analyzed, total_issues, overall_score, recommendations

## Workflow

1. Parse Python code
2. Run all analyzers
3. Detect patterns
4. Calculate metrics
5. Generate quality score
6. Create recommendations
7. Format report
