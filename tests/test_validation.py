"""Tests for validation modules."""


from socratic_analyzer.validation.code_structure_analyzer import CodeStructureAnalyzer
from socratic_analyzer.validation.dependency_validator import DependencyValidator
from socratic_analyzer.validation.syntax_validator import SyntaxValidator


class TestSyntaxValidator:
    """Test SyntaxValidator class."""

    def test_initialization(self):
        """Test validator initialization."""
        validator = SyntaxValidator()
        assert validator is not None
        assert hasattr(validator, "SUPPORTED_LANGUAGES")

    def test_supported_languages(self):
        """Test supported languages are defined."""
        validator = SyntaxValidator()
        assert ".py" in validator.SUPPORTED_LANGUAGES
        assert validator.SUPPORTED_LANGUAGES[".py"] == "python"
        assert ".js" in validator.SUPPORTED_LANGUAGES

    def test_validate_valid_python(self):
        """Test validating valid Python code."""
        validator = SyntaxValidator()
        code = "x = 1\nprint(x)"
        result = validator.validate(code, "python")

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["language"] == "python"

    def test_validate_invalid_python(self):
        """Test validating invalid Python code."""
        validator = SyntaxValidator()
        code = "x = \nprint(x)"  # Incomplete assignment
        result = validator.validate(code, "python")

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert result["language"] == "python"
        assert "line" in result["errors"][0]

    def test_validate_python_syntax_error(self):
        """Test Python syntax error detection."""
        validator = SyntaxValidator()
        code = "def foo(\n    pass"  # Incomplete function
        result = validator.validate(code, "python")

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_javascript_valid(self):
        """Test validating valid JavaScript."""
        validator = SyntaxValidator()
        code = "const x = 1;\nconsole.log(x);"
        result = validator.validate(code, "javascript")

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["language"] == "javascript"

    def test_validate_javascript_mismatched_braces(self):
        """Test detecting mismatched braces in JavaScript."""
        validator = SyntaxValidator()
        code = "function foo() { console.log('hi'); "  # Missing closing brace
        result = validator.validate(code, "javascript")

        assert result["valid"] is False
        assert any("brace" in e["message"].lower() for e in result["errors"])

    def test_validate_javascript_mismatched_parentheses(self):
        """Test detecting mismatched parentheses in JavaScript."""
        validator = SyntaxValidator()
        code = "foo(bar"  # Missing closing parenthesis
        result = validator.validate(code, "javascript")

        assert result["valid"] is False
        assert any("parenthes" in e["message"].lower() for e in result["errors"])

    def test_validate_unsupported_language(self):
        """Test validating unsupported language."""
        validator = SyntaxValidator()
        code = "some code"
        result = validator.validate(code, "ruby")

        assert result["valid"] is True  # Default behavior
        assert result["errors"] == []

    def test_validate_case_insensitive(self):
        """Test language parameter is case insensitive."""
        validator = SyntaxValidator()
        code = "x = 1"

        result1 = validator.validate(code, "python")
        result2 = validator.validate(code, "PYTHON")
        result3 = validator.validate(code, "Python")

        assert result1["valid"] == result2["valid"] == result3["valid"]


class TestCodeStructureAnalyzer:
    """Test CodeStructureAnalyzer class."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = CodeStructureAnalyzer()
        assert analyzer is not None

    def test_analyze_simple_python(self):
        """Test analyzing simple Python code."""
        analyzer = CodeStructureAnalyzer()
        code = "def foo():\n    pass\n\nclass Bar:\n    pass"
        result = analyzer.analyze(code, "python")

        assert result["language"] == "python"
        assert "foo" in result["functions"]
        assert "Bar" in result["classes"]

    def test_analyze_python_with_imports(self):
        """Test analyzing Python code with imports."""
        analyzer = CodeStructureAnalyzer()
        code = "import os\nimport sys\n\ndef main():\n    pass"
        result = analyzer.analyze(code, "python")

        assert "os" in result["imports"]
        assert "sys" in result["imports"]
        assert "main" in result["functions"]

    def test_analyze_python_lines_of_code(self):
        """Test that lines of code are counted."""
        analyzer = CodeStructureAnalyzer()
        code = "x = 1\ny = 2\nz = 3"
        result = analyzer.analyze(code, "python")

        assert "lines_of_code" in result
        assert result["lines_of_code"] == 3

    def test_analyze_python_syntax_error(self):
        """Test handling syntax errors during analysis."""
        analyzer = CodeStructureAnalyzer()
        code = "def foo(\n    invalid"
        result = analyzer.analyze(code, "python")

        assert "error" in result
        assert result["language"] == "python"

    def test_analyze_unsupported_language(self):
        """Test analyzing unsupported language."""
        analyzer = CodeStructureAnalyzer()
        code = "some code"
        result = analyzer.analyze(code, "ruby")

        assert result["classes"] == []
        assert result["functions"] == []
        assert result["imports"] == []

    def test_suggest_file_organization_many_classes(self):
        """Test file organization suggestion for many classes."""
        analyzer = CodeStructureAnalyzer()
        classes = "\n\n".join([f"class Class{i}:\n    pass" for i in range(6)])
        result = analyzer.suggest_file_organization(classes, "python")

        assert "suggestions" in result
        assert any("multiple files" in s.lower() for s in result["suggestions"])

    def test_suggest_file_organization_many_functions(self):
        """Test file organization suggestion for many functions."""
        analyzer = CodeStructureAnalyzer()
        functions = "\n\n".join([f"def func{i}():\n    pass" for i in range(11)])
        result = analyzer.suggest_file_organization(functions, "python")

        assert "suggestions" in result
        assert any("class" in s.lower() for s in result["suggestions"])

    def test_suggest_file_organization_syntax_error(self):
        """Test suggestion handling for syntax errors."""
        analyzer = CodeStructureAnalyzer()
        code = "def foo(\n    invalid"
        result = analyzer.suggest_file_organization(code, "python")

        assert result == {}


class TestDependencyValidator:
    """Test DependencyValidator class."""

    def test_initialization(self):
        """Test validator initialization."""
        validator = DependencyValidator()
        assert validator is not None

    def test_validate_python_imports(self):
        """Test validating Python imports."""
        validator = DependencyValidator()
        code = "import os\nimport sys\nfrom pathlib import Path"
        result = validator.validate(code, "python")

        assert result["language"] == "python"
        assert "os" in result["found_imports"]
        assert "sys" in result["found_imports"]
        assert "pathlib" in result["found_imports"]

    def test_validate_python_from_imports(self):
        """Test validating Python from imports."""
        validator = DependencyValidator()
        code = "from typing import List, Dict\nfrom collections import Counter"
        result = validator.validate(code, "python")

        assert "typing" in result["found_imports"]
        assert "collections" in result["found_imports"]

    def test_validate_python_multiple_imports(self):
        """Test validating multiple Python imports on one line."""
        validator = DependencyValidator()
        code = "import os, sys, json"
        result = validator.validate(code, "python")

        # The regex only captures the first import on each line
        assert "os" in result["found_imports"]

    def test_validate_javascript_imports(self):
        """Test validating JavaScript imports."""
        validator = DependencyValidator()
        code = "const React = require('react');\nconst { Component } = require('react');"
        result = validator.validate(code, "javascript")

        assert result["language"] == "javascript"
        assert "react" in result["found_imports"]

    def test_validate_javascript_requires(self):
        """Test validating JavaScript requires."""
        validator = DependencyValidator()
        code = "const express = require('express');\nconst fs = require('fs');"
        result = validator.validate(code, "javascript")

        assert "express" in result["found_imports"]
        assert "fs" in result["found_imports"]

    def test_validate_js_shorthand(self):
        """Test JavaScript using js language shorthand."""
        validator = DependencyValidator()
        code = 'import utils from "./utils";'
        result = validator.validate(code, "js")

        assert result["language"] == "javascript"

    def test_validate_unsupported_language(self):
        """Test validating unsupported language."""
        validator = DependencyValidator()
        code = "some code"
        result = validator.validate(code, "ruby")

        assert result["missing"] == []
        assert result["unused"] == []

    def test_validate_empty_code(self):
        """Test validating empty code."""
        validator = DependencyValidator()

        result_py = validator.validate("", "python")
        assert result_py["found_imports"] == []

        result_js = validator.validate("", "javascript")
        assert result_js["found_imports"] == []

    def test_validate_code_with_no_imports(self):
        """Test validating code with no imports."""
        validator = DependencyValidator()
        code = "x = 1\ny = 2\nprint(x + y)"

        result = validator.validate(code, "python")
        assert result["found_imports"] == []
