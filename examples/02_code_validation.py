"""
Code validation example.

Demonstrates how to validate dependencies and syntax using the library.
"""

from pathlib import Path

from socratic_analyzer.utils import DependencyValidator, SyntaxValidator


def main() -> None:
    """Run code validation example."""
    print("=" * 80)
    print("SOCRATIC ANALYZER - CODE VALIDATION EXAMPLE")
    print("=" * 80)
    print()

    # Example 1: Validate dependencies
    print("DEPENDENCY VALIDATION")
    print("-" * 80)
    validator = DependencyValidator()

    # Create a sample requirements.txt file
    sample_requirements = """
    requests>=2.28.0
    flask==2.2.0
    numpy>1.20
    """

    with open("sample_requirements.txt", "w") as f:
        f.write(sample_requirements)

    print("Sample requirements.txt:")
    print(sample_requirements)
    print()

    try:
        issues = validator.validate_dependencies("sample_requirements.txt")
        if issues:
            print("VALIDATION ISSUES FOUND:")
            for issue in issues:
                print(f"  • {issue['type']}: {issue['message']}")
        else:
            print("✓ No dependency issues found")
    except FileNotFoundError:
        print("Note: Sample requirements.txt was created for demonstration")
    finally:
        # Clean up
        Path("sample_requirements.txt").unlink(missing_ok=True)

    print()

    # Example 2: Validate Python syntax
    print("SYNTAX VALIDATION")
    print("-" * 80)
    syntax_validator = SyntaxValidator()

    # Create sample Python files
    good_code = '''
def hello_world():
    """Print hello world."""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
'''

    bad_code = '''
def hello_world()
    print("Missing colon")

if __name__ == "__main__"
    hello_world()
'''

    # Write sample files
    Path("good_example.py").write_text(good_code)
    Path("bad_example.py").write_text(bad_code)

    print("Validating good_example.py...")
    good_errors = syntax_validator.validate_syntax("good_example.py")
    if good_errors:
        print(f"  Found {len(good_errors)} issues:")
        for error in good_errors:
            print(f"    • {error}")
    else:
        print("  ✓ No syntax errors found")

    print()

    print("Validating bad_example.py...")
    bad_errors = syntax_validator.validate_syntax("bad_example.py")
    if bad_errors:
        print(f"  Found {len(bad_errors)} issues:")
        for error in bad_errors:
            print(f"    • {error}")
    else:
        print("  ✓ No syntax errors found")

    print()

    # Clean up
    Path("good_example.py").unlink(missing_ok=True)
    Path("bad_example.py").unlink(missing_ok=True)

    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
