from __future__ import annotations

"""
Monitoring and token usage models for Socrates AI
"""

import datetime
from dataclasses import dataclass, asdict


@dataclass
class TokenUsage:
    @staticmethod
    def from_dict(data: dict) -> "TokenUsage":
        """Deserialize from dictionary."""
        return TokenUsage(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        from dataclasses import asdict
        return asdict(self)


    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: datetime.datetime
    model: str = "claude-opus-4-5-20251101"
    cost_estimate: float = 0.0
    @staticmethod
    def from_dict(data: dict) -> "TokenUsage":
        """Deserialize from dictionary."""
        return TokenUsage(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        from dataclasses import asdict
        return asdict(self)

