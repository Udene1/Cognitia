"""Durable archival boundary for observed environmental evidence.

Raw observations are evidence, not knowledge. This adapter makes the existing
observation store usable at acquisition boundaries without promoting anything
into validated cognition.
"""
from __future__ import annotations

from pathlib import Path

from .environment import EnvironmentObservation
from .observation import Observation
from .memory.observation_sqlite import SQLiteObservationStore


class DurableEvidenceArchive:
    """Persist exact observations so later cognition can reinterpret them."""

    def __init__(self, path: str | Path) -> None:
        self._store = SQLiteObservationStore(path)

    def close(self) -> None:
        self._store.close()

    def __enter__(self) -> "DurableEvidenceArchive":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def retain(self, observation: Observation) -> Observation:
        return self._store.ingest(observation)

    def retain_environment(self, observation: EnvironmentObservation) -> Observation:
        """Archive an acquired environment observation without validating it."""
        metadata = tuple(observation.metadata) + (("reliability", str(observation.reliability)),)
        retained = Observation.create(
            environment=observation.source,
            kind="environment_observation",
            subject=observation.id,
            payload=observation.content,
            source_uri=dict(observation.metadata).get("url"),
            parent_ids=(),
            metadata=metadata,
        )
        return self.retain(retained)

    def retain_many(self, observations: tuple[Observation, ...]) -> tuple[Observation, ...]:
        return tuple(self.retain(observation) for observation in observations)

    def get(self, observation_id: str) -> Observation:
        return self._store.get(observation_id)

    def all(self) -> tuple[Observation, ...]:
        return self._store.all()

    def by_environment(self, environment: str) -> tuple[Observation, ...]:
        return self._store.by_environment(environment)
