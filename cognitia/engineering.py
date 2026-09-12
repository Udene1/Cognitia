"""Engineering-environment observations that can become Cognitia experiences.

This module deliberately records what happened without declaring that a development
choice was correct. Outcomes remain explicit so learning can distinguish attempts
from successful patterns.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping

from .memory.experience import Experience, Outcome


@dataclass(frozen=True)
class EngineeringEvent:
    """A structured observation from the process of building Cognitia."""

    kind: str
    context: Mapping[str, object]
    action: str
    observation: Mapping[str, object]
    outcome: Outcome
    id: str = field(default="")
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("event kind is required")
        if not self.action.strip():
            raise ValueError("event action is required")
        if not self.observation:
            raise ValueError("event observation is required")

    def to_experience(self) -> Experience:
        """Convert an engineering event into Cognitia's canonical experience form."""
        context = dict(self.context)
        context["environment"] = "engineering"
        context["event_kind"] = self.kind
        if self.id:
            context["event_id"] = self.id
        return Experience(
            context=context,
            action=self.action,
            observation=dict(self.observation),
            outcome=self.outcome,
            occurred_at=self.occurred_at,
        )


class EngineeringExperienceRecorder:
    """Bridge engineering observations into the existing append-only experience memory."""

    def __init__(self, store) -> None:
        self._store = store

    def record(self, event: EngineeringEvent) -> Experience:
        experience = event.to_experience()
        return self._store.record(experience)

    def record_outcome(
        self,
        *,
        kind: str,
        context: Mapping[str, object],
        action: str,
        observation: Mapping[str, object],
        outcome: Outcome,
        occurred_at: datetime | None = None,
    ) -> Experience:
        """Record one complete engineering episode in canonical memory."""
        return self.record(
            EngineeringEvent(
                kind=kind,
                context=context,
                action=action,
                observation=observation,
                outcome=outcome,
                occurred_at=occurred_at or datetime.now(timezone.utc),
            )
        )
