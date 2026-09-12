"""Core world-state and evidence primitives for Cognitia v0.01."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Evidence:
    """An observation that can change the system's world state."""

    proposition: str
    value: Any
    source: str
    reliability: float = 1.0
    observed_at: datetime = field(default_factory=utc_now)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be between 0 and 1")


@dataclass(frozen=True)
class Belief:
    """A proposition held by Cognitia, separate from raw observations."""

    proposition: str
    confidence: float
    supporting_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class WorldState:
    """Immutable snapshot of Cognitia's current internal world representation."""

    facts: Mapping[str, Any] = field(default_factory=dict)
    beliefs: Mapping[str, Belief] = field(default_factory=dict)
    evidence: tuple[Evidence, ...] = ()
    version: int = 0

    def with_evidence(self, evidence: Evidence) -> "WorldState":
        """Apply one observation and return a new state snapshot.

        v0.01 uses a deliberately simple confidence rule: evidence reliability
        becomes the confidence for the observed proposition. More sophisticated
        belief revision belongs to a later version.
        """
        facts = dict(self.facts)
        beliefs = dict(self.beliefs)
        facts[evidence.proposition] = evidence.value
        beliefs[evidence.proposition] = Belief(
            proposition=evidence.proposition,
            confidence=evidence.reliability,
            supporting_evidence=(evidence.id,),
        )
        return replace(
            self,
            facts=facts,
            beliefs=beliefs,
            evidence=self.evidence + (evidence,),
            version=self.version + 1,
        )
