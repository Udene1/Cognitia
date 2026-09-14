"""Durable observation records: sources are observed, then cognition is derived.

An observation is not itself knowledge. It is retained evidence about an observed
state/event so that later learning can be audited, reinterpreted, contradicted,
or repeated without having to rediscover the source artifact.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable


@dataclass(frozen=True)
class Observation:
    id: str
    environment: str
    kind: str
    subject: str
    payload: str
    source_uri: str | None = None
    observed_at: str | None = None
    parent_ids: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        *,
        environment: str,
        kind: str,
        subject: str,
        payload: str,
        source_uri: str | None = None,
        observed_at: str | None = None,
        parent_ids: Iterable[str] = (),
        metadata: Iterable[tuple[str, str]] = (),
    ) -> "Observation":
        canonical = "|".join((environment, kind, subject, payload, source_uri or "", observed_at or ""))
        observation_id = sha256(canonical.encode("utf-8")).hexdigest()
        return cls(observation_id, environment, kind, subject, payload, source_uri,
                   observed_at, tuple(parent_ids), tuple(metadata))


class ObservationLedger:
    """Append-only in-memory ledger suitable for persistence adapters.

    The ledger deliberately stores observations separately from learned knowledge.
    A later durable backend can serialize the exact records without changing the
    observation/experience/knowledge boundary.
    """

    def __init__(self, observations: Iterable[Observation] = ()) -> None:
        self._items: dict[str, Observation] = {item.id: item for item in observations}

    def ingest(self, observation: Observation) -> Observation:
        existing = self._items.get(observation.id)
        if existing is not None and existing != observation:
            raise ValueError(f"observation id collision: {observation.id}")
        self._items[observation.id] = observation
        return observation

    def get(self, observation_id: str) -> Observation:
        return self._items[observation_id]

    def all(self) -> tuple[Observation, ...]:
        return tuple(self._items.values())

    def by_environment(self, environment: str) -> tuple[Observation, ...]:
        return tuple(item for item in self._items.values() if item.environment == environment)

    def link_experience(self, observation_ids: Iterable[str]) -> tuple[Observation, ...]:
        return tuple(self.get(item) for item in observation_ids)
