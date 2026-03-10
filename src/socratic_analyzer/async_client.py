"""Async analyzer client interface."""

import asyncio
from typing import List, Optional

from socratic_analyzer.client import AnalyzerClient
from socratic_analyzer.models import Analysis, AnalyzerConfig


class AsyncAnalyzerClient(AnalyzerClient):
    """Async analyzer client interface.

    Provides async/await support for analyzing Python code.
    """

    async def analyze_file_async(self, file_path: str) -> Analysis:
        """Analyze a single Python file asynchronously.

        Args:
            file_path: Path to the Python file

        Returns:
            Analysis object with results

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze_file, file_path)

    async def analyze_code_async(
        self, code: str, file_path: str = "unknown.py"
    ) -> Analysis:
        """Analyze Python code asynchronously.

        Args:
            code: Python source code
            file_path: Path to file (for reporting, optional)

        Returns:
            Analysis object with results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.analyze_code, code, file_path
        )

    async def analyze_files_async(self, file_paths: List[str]) -> List[Analysis]:
        """Analyze multiple Python files asynchronously.

        Args:
            file_paths: List of paths to Python files

        Returns:
            List of Analysis objects

        Raises:
            FileNotFoundError: If any file doesn't exist
            IOError: If any file can't be read
        """
        tasks = [self.analyze_file_async(fp) for fp in file_paths]
        return await asyncio.gather(*tasks)

    async def batch_analyze_code_async(
        self, code_samples: List[tuple]
    ) -> List[Analysis]:
        """Analyze multiple code samples asynchronously.

        Args:
            code_samples: List of (code, file_path) tuples

        Returns:
            List of Analysis objects
        """
        tasks = [
            self.analyze_code_async(code, fp or "unknown.py")
            for code, fp in code_samples
        ]
        return await asyncio.gather(*tasks)

    async def generate_report_async(
        self, analysis: Analysis, format: str = "text"
    ) -> str:
        """Generate formatted report asynchronously.

        Args:
            analysis: Analysis object
            format: Report format ("text", "json", "markdown")

        Returns:
            Formatted report string
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.generate_report, analysis, format
        )

    async def get_recommendations_async(self, analysis: Analysis) -> List[str]:
        """Get actionable recommendations asynchronously.

        Args:
            analysis: Analysis object

        Returns:
            List of recommendations
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_recommendations, analysis)
