"""Environment interfaces for standalone Cognitia capabilities.

An environment source supplies observations. It is deliberately separate from
reasoning: a future web adapter can implement this interface without becoming
Cognitia's intelligence or requiring an LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EnvironmentObservation:
    id: str
    source: str
    content: str
    reliability: float = 1.0
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.source or not self.content:
            raise ValueError("observation id, source and content are required")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be between 0 and 1")


class EnvironmentSource(Protocol):
    """Capability boundary for external evidence acquisition."""

    def observe(self, objective: str, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        ...


class NullEnvironmentSource:
    """Explicitly unavailable environment; useful as a safe default."""

    def observe(self, objective: str, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        return ()
