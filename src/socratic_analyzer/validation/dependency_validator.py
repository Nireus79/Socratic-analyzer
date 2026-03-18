"""Dependency Validator - Validate project dependencies."""

import logging
import re

logger = logging.getLogger(__name__)


class DependencyValidator:
    """Validate project dependencies"""

    def __init__(self):
        logger.debug("DependencyValidator initialized")

    def validate(self, code: str, language: str = "python") -> dict:
        """Validate dependencies"""
        if language == "python":
            return self._validate_python(code)
        elif language in ["javascript", "js"]:
            return self._validate_javascript(code)
        return {"missing": [], "unused": []}

    def _validate_python(self, code: str) -> dict:
        """Find Python imports"""
        imports = set(re.findall(r"^(?:from|import)\s+(\w+)", code, re.MULTILINE))
        return {"found_imports": list(imports), "language": "python"}

    def _validate_javascript(self, code: str) -> dict:
        """Find JavaScript imports"""
        imports = set(re.findall(r'(?:import|require)\(["\']([^"\']+)["\']\)', code))
        return {"found_imports": list(imports), "language": "javascript"}
