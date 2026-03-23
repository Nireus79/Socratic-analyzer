"""Dependency Validator - Validate project dependencies."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class DependencyValidator:
    """Validate project dependencies"""

    def __init__(self) -> None:
        logger.debug("DependencyValidator initialized")

    def validate(self, code: str, language: str = "python") -> dict[str, Any]:
        """Validate dependencies"""
        if language == "python":
            return self._validate_python(code)
        elif language in ["javascript", "js"]:
            return self._validate_javascript(code)
        return {"missing": [], "unused": []}

    def _validate_python(self, code: str) -> dict[str, Any]:
        """Find Python imports"""
        imports = set(re.findall(r"^(?:from|import)\s+(\w+)", code, re.MULTILINE))
        return {"found_imports": list(imports), "language": "python"}

    def _validate_javascript(self, code: str) -> dict[str, Any]:
        """Find JavaScript imports"""
        imports = set(re.findall(r'(?:import|require)\(["\']([^"\']+)["\']\)', code))
        return {"found_imports": list(imports), "language": "javascript"}
