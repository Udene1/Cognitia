"""Traceable discovery records from observation through reproduction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .durable import DurableEvent, SQLiteCognitiveJournal


@dataclass(frozen=True)
class DiscoveryArtifact:
    """Immutable research record; status describes evidence, not truth."""

    id: str
    title: str
    observation_ids: tuple[str, ...] = ()
    model_id: str = ""
    gap_id: str = ""
    hypothesis_ids: tuple[str, ...] = ()
    prediction_ids: tuple[str, ...] = ()
    experiment_id: str = ""
    outcome: str = "pending"
    epistemic_status: str = "hypothesis"
    reproduction_status: str = "not_attempted"

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.title.strip():
            raise ValueError("discovery artifact id and title are required")
        if not self.observation_ids:
            raise ValueError("a discovery artifact needs at least one observation")

    @property
    def is_ready_for_reproduction(self) -> bool:
        return bool(self.experiment_id and self.outcome not in {"pending", ""})

    def with_outcome(self, outcome: str, *, epistemic_status: str) -> "DiscoveryArtifact":
        if not outcome.strip() or not epistemic_status.strip():
            raise ValueError("outcome and epistemic status are required")
        return DiscoveryArtifact(self.id, self.title, self.observation_ids, self.model_id, self.gap_id,
                                 self.hypothesis_ids, self.prediction_ids, self.experiment_id,
                                 outcome, epistemic_status, self.reproduction_status)

    def with_reproduction(self, status: str) -> "DiscoveryArtifact":
        if not status.strip():
            raise ValueError("reproduction status is required")
        return DiscoveryArtifact(self.id, self.title, self.observation_ids, self.model_id, self.gap_id,
                                 self.hypothesis_ids, self.prediction_ids, self.experiment_id,
                                 self.outcome, self.epistemic_status, status)


class DurableDiscoveryArtifacts:
    """Persist every research stage as evidence; only validated knowledge is promoted separately."""

    def __init__(self, journal: SQLiteCognitiveJournal) -> None:
        self.journal = journal

    def record(self, artifact: DiscoveryArtifact) -> DurableEvent:
        return self.journal.append(DurableEvent(
            kind="discovery_artifact", source="discovery_lifecycle",
            payload={"id": artifact.id, "title": artifact.title, "observation_ids": list(artifact.observation_ids),
                     "model_id": artifact.model_id, "gap_id": artifact.gap_id, "hypothesis_ids": list(artifact.hypothesis_ids),
                     "prediction_ids": list(artifact.prediction_ids), "experiment_id": artifact.experiment_id,
                     "outcome": artifact.outcome, "epistemic_status": artifact.epistemic_status,
                     "reproduction_status": artifact.reproduction_status},
        ))

    def all(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("discovery_artifact"))
