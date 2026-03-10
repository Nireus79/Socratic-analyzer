# Socratic Analyzer - API Reference

Complete API documentation for Socratic Analyzer.

## Core Classes

### AnalyzerClient

Main synchronous analyzer client.

```python
class AnalyzerClient:
    def __init__(self, config: Optional[AnalyzerConfig] = None) -> None:
        """Initialize analyzer client."""

    def analyze_file(self, file_path: str) -> Analysis:
        """Analyze a Python file."""

    def analyze_code(self, code: str, file_path: str = "unknown.py") -> Analysis:
        """Analyze Python code string."""

    def generate_report(self, analysis: Analysis, format: str = "text") -> str:
        """Generate formatted report (text, json, markdown)."""

    def get_recommendations(self, analysis: Analysis) -> List[str]:
        """Get improvement recommendations."""
```

### AsyncAnalyzerClient

Asynchronous version of AnalyzerClient.

```python
class AsyncAnalyzerClient(AnalyzerClient):
    async def analyze_file_async(self, file_path: str) -> Analysis:
        """Analyze file asynchronously."""

    async def analyze_code_async(self, code: str, file_path: str = "unknown.py") -> Analysis:
        """Analyze code asynchronously."""

    async def analyze_files_async(self, file_paths: List[str]) -> List[Analysis]:
        """Analyze multiple files asynchronously."""

    async def batch_analyze_code_async(self, code_samples: List[tuple]) -> List[Analysis]:
        """Analyze multiple code samples asynchronously."""

    async def generate_report_async(self, analysis: Analysis, format: str = "text") -> str:
        """Generate report asynchronously."""

    async def get_recommendations_async(self, analysis: Analysis) -> List[str]:
        """Get recommendations asynchronously."""
```

## Data Models

### Analysis

Result of analyzing a single file or code sample.

```python
@dataclass
class Analysis:
    file_path: str                          # Path to analyzed file
    file_size: int                          # File size in bytes
    language: str                           # Programming language
    issues: List[CodeIssue]                # Detected issues
    metrics: List[MetricResult]            # Code metrics
    patterns: List[str]                    # Detected patterns
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Properties
    @property
    def total_issues(self) -> int:          # Total number of issues
    @property
    def critical_issues(self) -> int:       # Number of critical issues
    @property
    def high_issues(self) -> int:           # Number of high severity issues
```

### CodeIssue

A single code issue detected by analysis.

```python
@dataclass
class CodeIssue:
    issue_type: str                         # Type of issue
    severity: str                           # Severity level
    message: str                            # Issue description
    location: str                           # Location in code
    suggestion: Optional[str] = None        # Improvement suggestion
```

### MetricResult

A code metric measurement.

```python
@dataclass
class MetricResult:
    name: str                               # Metric name
    value: float                            # Metric value
    threshold: Optional[float]             # Threshold value
    status: str                             # ok, warning, or error
    description: Optional[str] = None      # Metric description
```

### AnalyzerConfig

Configuration for analyzer behavior.

```python
@dataclass
class AnalyzerConfig:
    max_complexity: int = 10               # Max cyclomatic complexity
    max_line_length: int = 120             # Max line length
    include_metrics: bool = True           # Include code metrics
    analyze_types: bool = True             # Analyze type hints
    analyze_docstrings: bool = True        # Check docstrings
```

## Analyzers

### StaticAnalyzer

Detects static code issues and violations.

```python
class StaticAnalyzer(BaseAnalyzer):
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Detect static code issues."""
```

Detects:
- Unused variables
- Missing docstrings
- Long lines
- Empty blocks
- Wildcard imports

### ComplexityAnalyzer

Calculates code complexity metrics.

```python
class ComplexityAnalyzer(BaseAnalyzer):
    def __init__(self, max_complexity: int = 10):
        """Initialize with complexity threshold."""

    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze complexity."""
```

Detects:
- High cyclomatic complexity
- Deep nesting
- High function length

### MetricsAnalyzer

Calculates code metrics.

```python
class MetricsAnalyzer(BaseAnalyzer):
    def calculate_metrics(self, code: str) -> List[MetricResult]:
        """Calculate code metrics."""
```

Calculates:
- Lines of code
- Maintainability index
- Function/class metrics

### ImportAnalyzer

Analyzes import organization.

```python
class ImportAnalyzer(BaseAnalyzer):
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze imports."""
```

### PatternAnalyzer

Detects design patterns.

```python
class PatternAnalyzer(BaseAnalyzer):
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Detect patterns."""
```

Detects:
- Singleton
- Factory
- Decorator
- Context Manager
- Observer
- Strategy
- Callback
- Template Method

### CodeSmellDetector

Detects code smells.

```python
class CodeSmellDetector(BaseAnalyzer):
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Detect code smells."""
```

### PerformanceAnalyzer

Detects performance issues.

```python
class PerformanceAnalyzer(BaseAnalyzer):
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze performance."""
```

## Utilities

### QualityScorer

Calculates overall code quality.

```python
class QualityScorer:
    @classmethod
    def calculate_quality_score(cls, analysis: Analysis) -> float:
        """Get quality score (0-100)."""

    @classmethod
    def get_quality_rating(cls, score: float) -> str:
        """Get rating (Excellent to Critical)."""

    @classmethod
    def create_quality_report(cls, analysis: Analysis) -> Dict[str, Any]:
        """Create comprehensive quality report."""
```

## Framework Integrations

### Openclaw Skill

```python
from socratic_analyzer.integrations.openclaw import SocraticAnalyzerSkill

class SocraticAnalyzerSkill:
    def analyze_code(self, code: str, file_path: str = "unknown.py") -> Dict:
        """Analyze code."""

    def get_quality_score(self, code: str) -> float:
        """Get quality score."""

    def get_recommendations(self, code: str) -> List[str]:
        """Get recommendations."""
```

### LangChain Tools

```python
from socratic_analyzer.integrations.langchain import (
    SocraticAnalyzerTool,
    SocraticAnalyzerQualityTool,
    SocraticAnalyzerIssuesTool,
    SocraticAnalyzerRecommendationsTool,
    create_analyzer_tools,
)

# Use in LangChain agents
tools = create_analyzer_tools()
```

## Exceptions

- `AnalyzerError` - Base analyzer exception
- `AnalysisError` - Error during analysis
- `ConfigurationError` - Invalid configuration
- `ParsingError` - Code parsing error
- `PatternDetectionError` - Pattern detection error
- `ReportError` - Report generation error
- `ReportFormatError` - Invalid report format

## Report Formats

### Text Format

Human-readable plain text report with sections for summary, issues, metrics, and patterns.

### JSON Format

Machine-readable JSON with all analysis results, suitable for programmatic access.

### Markdown Format

Markdown-formatted report suitable for documentation and GitHub.

## Return Values

All analyzers return `List[CodeIssue]` containing:
- `issue_type`: Type of issue (e.g., "complexity", "smell")
- `severity`: Issue severity ("critical", "high", "medium", "low", "info")
- `message`: Human-readable issue description
- `location`: Location in code (file:line:col)
- `suggestion`: Optional improvement suggestion

## Performance Characteristics

- Small code (< 500 lines): < 100ms
- Medium code (500-5000 lines): < 500ms
- Large code (> 5000 lines): < 2000ms
- Report generation: < 100ms
- Recommendations: < 50ms

## Thread Safety

- `AnalyzerClient` is thread-safe (reads configuration only)
- `AsyncAnalyzerClient` supports async/await pattern
- No global state is modified during analysis
