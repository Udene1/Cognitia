"""Experiences recorded from actions and their consequences."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Outcome:
    """What happened after an action; positive, negative, or neutral."""

    kind: str
    description: str
    value: float | None = None

    def __post_init__(self) -> None:
        if self.kind not in {"positive", "negative", "neutral"}:
            raise ValueError("outcome kind must be positive, negative, or neutral")
        if not self.description.strip():
            raise ValueError("outcome description must not be empty")


@dataclass(frozen=True)
class Experience:
    """A complete action -> observation -> consequence episode."""

    context: dict[str, object]
    action: str
    observation: dict[str, object]
    outcome: Outcome
    id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ExperienceStore:
    """Append-only experience memory for v0.01."""

    def __init__(self) -> None:
        self._experiences: list[Experience] = []

    def record(self, experience: Experience) -> Experience:
        self._experiences.append(experience)
        return experience

    def all(self) -> tuple[Experience, ...]:
        return tuple(self._experiences)
