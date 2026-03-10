"""Tests for LangChain integration."""

import pytest

# Try to import LangChain tools
try:
    from socratic_analyzer.integrations.langchain import (
        SocraticAnalyzerTool,
        SocraticAnalyzerQualityTool,
        SocraticAnalyzerIssuesTool,
        SocraticAnalyzerRecommendationsTool,
        create_analyzer_tools,
    )

    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


@pytest.mark.skipif(not HAS_LANGCHAIN, reason="LangChain not installed")
class TestSocraticAnalyzerTool:
    """Test SocraticAnalyzerTool."""

    @pytest.fixture
    def tool(self) -> SocraticAnalyzerTool:
        """Provide analyzer tool."""
        return SocraticAnalyzerTool()

    @pytest.fixture
    def sample_code(self) -> str:
        """Sample Python code."""
        return '''
def add(x, y):
    """Add two numbers."""
    return x + y

class Calculator:
    """Simple calculator."""

    def multiply(self, a, b):
        return a * b
'''

    def test_tool_initialization(self, tool) -> None:
        """Test tool initialization."""
        assert tool.name == "socratic_analyzer"
        assert tool.client is not None
        assert len(tool.description) > 0

    def test_tool_run(self, tool, sample_code) -> None:
        """Test tool execution."""
        result = tool._run(sample_code)

        assert isinstance(result, str)
        assert "Quality Score" in result
        assert "/100" in result

    def test_tool_run_with_issues(self, tool) -> None:
        """Test tool with problematic code."""
        code = '''
def bad():
    if x:
        if y:
            pass
'''
        result = tool._run(code)

        assert isinstance(result, str)
        assert "Quality Score" in result

    def test_quality_score_tool(self) -> None:
        """Test quality score tool."""
        tool = SocraticAnalyzerQualityTool()

        assert tool.name == "socratic_quality_score"
        code = "x = 1\ny = 2\n"
        result = tool._run(code)

        assert "Quality Score" in result
        assert "/100" in result

    def test_issues_tool(self) -> None:
        """Test issues detection tool."""
        tool = SocraticAnalyzerIssuesTool()

        assert tool.name == "socratic_detect_issues"
        code = '''
def bad():
    try:
        pass
    except:
        pass
'''
        result = tool._run(code)

        assert isinstance(result, str)
        # Should either have issues or say no issues
        assert "issue" in result.lower() or "error" in result.lower()

    def test_recommendations_tool(self) -> None:
        """Test recommendations tool."""
        tool = SocraticAnalyzerRecommendationsTool()

        assert tool.name == "socratic_recommendations"
        code = "x = 1\n"
        result = tool._run(code)

        assert isinstance(result, str)
        assert "Recommendation" in result

    def test_create_analyzer_tools(self) -> None:
        """Test creating all tools."""
        tools = create_analyzer_tools()

        assert len(tools) == 4
        tool_names = [t.name for t in tools]
        assert "socratic_analyzer" in tool_names
        assert "socratic_quality_score" in tool_names
        assert "socratic_detect_issues" in tool_names
        assert "socratic_recommendations" in tool_names

    def test_tool_error_handling(self, tool) -> None:
        """Test tool error handling with invalid code."""
        invalid_code = "def broken(\n  invalid"
        result = tool._run(invalid_code)

        assert isinstance(result, str)
        # Should not crash, should return some result
        assert len(result) > 0

    def test_quality_tool_clean_code(self) -> None:
        """Test quality tool with clean code."""
        tool = SocraticAnalyzerQualityTool()

        clean_code = '''
def clean_function(x, y):
    """Clean function."""
    result = x + y
    return result
'''
        result = tool._run(clean_code)

        assert "Quality Score" in result
        assert isinstance(result, str)

    def test_issues_tool_clean_code(self) -> None:
        """Test issues tool with clean code."""
        tool = SocraticAnalyzerIssuesTool()

        clean_code = "def foo():\n    return 42\n"
        result = tool._run(clean_code)

        assert isinstance(result, str)
        # Should say no issues or have few issues
        assert len(result) > 0

    def test_recommendations_tool_problematic_code(self) -> None:
        """Test recommendations tool with problematic code."""
        tool = SocraticAnalyzerRecommendationsTool()

        bad_code = '''
def complex(a, b, c, d, e, f):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return f
    return 0
'''
        result = tool._run(bad_code)

        assert isinstance(result, str)
        assert "Recommendation" in result

    def test_tool_with_custom_config(self) -> None:
        """Test tool with custom configuration."""
        tool = SocraticAnalyzerTool(max_complexity=5, include_metrics=False)

        assert tool.client.config.max_complexity == 5
        assert tool.client.config.include_metrics is False
