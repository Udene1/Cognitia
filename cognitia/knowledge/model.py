"""Core knowledge objects used by Cognitia."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class KnowledgeSource:
    """Provenance for a piece of knowledge."""

    kind: str
    reference: str
    reliability: float = 1.0

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("source kind must not be empty")
        if not self.reference.strip():
            raise ValueError("source reference must not be empty")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("source reliability must be between 0 and 1")


@dataclass(frozen=True)
class KnowledgeItem:
    """A proposition Cognitia can reason about.

    Knowledge is deliberately distinct from belief: this object records what was
    learned and where it came from; a later reasoning layer decides how strongly
    the proposition should be believed in a particular context.
    """

    subject: str
    predicate: str
    value: object
    source: KnowledgeSource
    id: str = field(default_factory=lambda: str(uuid4()))
    learned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scope: str = "general"

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("subject must not be empty")
        if not self.predicate.strip():
            raise ValueError("predicate must not be empty")
        if not self.scope.strip():
            raise ValueError("scope must not be empty")
