"""Abstract base class for code analyzers."""

from abc import ABC, abstractmethod
from typing import List

from socratic_analyzer.models import CodeIssue


class BaseAnalyzer(ABC):
    """Abstract base class for code analyzers."""

    @abstractmethod
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        """Analyze code and return list of issues.

        Args:
            code: Source code to analyze
            file_path: Path to the file (for location reporting)

        Returns:
            List of CodeIssue objects found
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Analyzer name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Analyzer description."""
        pass

    def _format_location(self, file_path: str, line_num: int, col_num: int = 0) -> str:
        """Format location string.

        Args:
            file_path: Path to file
            line_num: Line number (1-indexed)
            col_num: Column number (optional, 1-indexed)

        Returns:
            Formatted location string
        """
        if col_num > 0:
            return f"{file_path}:{line_num}:{col_num}"
        return f"{file_path}:{line_num}"
