"""Example: Using Socratic Analyzer with LangChain."""

from socratic_analyzer.integrations.langchain import (
    SocraticAnalyzerTool,
    SocraticAnalyzerQualityTool,
    SocraticAnalyzerIssuesTool,
    SocraticAnalyzerRecommendationsTool,
    create_analyzer_tools,
)

# Sample code to analyze
sample_code = '''
def calculate_total(items, multiplier=1):
    """Calculate total with multiplier."""
    total = 0
    for item in items:
        total += item * multiplier  # Performance issue
    return total

def check_status(code, age, status):
    """Check status with nested conditions."""
    if code > 0:
        if age > 18:
            if status == "active":
                return True
    return False

global_counter = 0

def increment():
    """Increment global counter."""
    global global_counter
    global_counter += 1
'''


def main() -> None:
    """Run LangChain integration examples."""
    print("=" * 80)
    print("SOCRATIC ANALYZER - LANGCHAIN INTEGRATION EXAMPLE")
    print("=" * 80)
    print()

    # Example 1: Using main analyzer tool
    print("1. MAIN ANALYZER TOOL")
    print("-" * 80)
    tool = SocraticAnalyzerTool()
    result = tool._run(sample_code)
    print(result)
    print()

    # Example 2: Quality score tool
    print("2. QUALITY SCORE TOOL")
    print("-" * 80)
    quality_tool = SocraticAnalyzerQualityTool()
    result = quality_tool._run(sample_code)
    print(result)
    print()

    # Example 3: Issues detection tool
    print("3. ISSUES DETECTION TOOL")
    print("-" * 80)
    issues_tool = SocraticAnalyzerIssuesTool()
    result = issues_tool._run(sample_code)
    print(result)
    print()

    # Example 4: Recommendations tool
    print("4. RECOMMENDATIONS TOOL")
    print("-" * 80)
    rec_tool = SocraticAnalyzerRecommendationsTool()
    result = rec_tool._run(sample_code)
    print(result)
    print()

    # Example 5: Creating all tools at once
    print("5. CREATE ALL TOOLS")
    print("-" * 80)
    all_tools = create_analyzer_tools()
    print(f"Created {len(all_tools)} tools:")
    for tool in all_tools:
        print(f"  - {tool.name}: {tool.description[:60]}...")
    print()

    # Example 6: Tool integration example (simulated LangChain usage)
    print("6. SIMULATED LANGCHAIN AGENT USAGE")
    print("-" * 80)
    print("In a real LangChain agent:")
    print("  from langchain.agents import initialize_agent, AgentType")
    print("  from socratic_analyzer.integrations.langchain import create_analyzer_tools")
    print()
    print("  tools = create_analyzer_tools()")
    print("  agent = initialize_agent(")
    print("      tools,")
    print("      llm,")
    print("      agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION")
    print("  )")
    print()
    print("  # Then use the agent:")
    print("  result = agent.run('Analyze this code: ...')")
    print()

    # Example 7: Tool metadata
    print("7. TOOL METADATA")
    print("-" * 80)
    for tool in all_tools:
        print(f"Tool: {tool.name}")
        print(f"  Description: {tool.description}")
        print()

    # Example 8: Comparing code with tools
    print("8. CODE COMPARISON WITH TOOLS")
    print("-" * 80)
    bad_code = '''
def process(x, y, z, a, b):
    global_state = 0
    try:
        result = x + y + z + a + b
    except:
        pass
    return result
'''

    good_code = '''
def process(x, y, z, a, b):
    """Process numbers."""
    result = x + y + z + a + b
    return result
'''

    print("Bad Code Analysis:")
    bad_result = tool._run(bad_code)
    bad_lines = bad_result.split("\n")[:3]
    print("\n".join(bad_lines))
    print()

    print("Good Code Analysis:")
    good_result = tool._run(good_code)
    good_lines = good_result.split("\n")[:3]
    print("\n".join(good_lines))
    print()

    print("=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
