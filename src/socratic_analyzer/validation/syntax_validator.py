"""Syntax Validator - Multi-language code syntax validation."""

import logging

logger = logging.getLogger(__name__)


class SyntaxValidator:
    """Validate code syntax for multiple languages"""

    SUPPORTED_LANGUAGES = {".py": "python", ".js": "javascript", ".java": "java", ".cpp": "cpp"}

    def __init__(self):
        logger.debug("SyntaxValidator initialized")

    def validate(self, code: str, language: str) -> dict:
        """Validate code syntax"""
        if language.lower() == "python":
            return self._validate_python(code)
        elif language.lower() in ["javascript", "js"]:
            return self._validate_javascript(code)
        return {"valid": True, "errors": []}

    def _validate_python(self, code: str) -> dict:
        """Validate Python syntax"""
        try:
            compile(code, "<string>", "exec")
            return {"valid": True, "errors": [], "language": "python"}
        except SyntaxError as e:
            return {"valid": False, "errors": [{"line": e.lineno, "message": str(e)}], "language": "python"}

    def _validate_javascript(self, code: str) -> dict:
        """Validate JavaScript syntax"""
        errors = []
        if code.count("{") != code.count("}"):
            errors.append({"line": -1, "message": "Mismatched braces"})
        if code.count("(") != code.count(")"):
            errors.append({"line": -1, "message": "Mismatched parentheses"})
        return {"valid": len(errors) == 0, "errors": errors, "language": "javascript"}
