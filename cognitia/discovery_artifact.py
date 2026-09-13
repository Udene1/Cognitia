"""Traceable records for investigations from observation to reproduction."""
from __future__ import annotations

from dataclasses import dataclass


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
        return DiscoveryArtifact(
            id=self.id,
            title=self.title,
            observation_ids=self.observation_ids,
            model_id=self.model_id,
            gap_id=self.gap_id,
            hypothesis_ids=self.hypothesis_ids,
            prediction_ids=self.prediction_ids,
            experiment_id=self.experiment_id,
            outcome=outcome,
            epistemic_status=epistemic_status,
            reproduction_status=self.reproduction_status,
        )

    def with_reproduction(self, status: str) -> "DiscoveryArtifact":
        if not status.strip():
            raise ValueError("reproduction status is required")
        return DiscoveryArtifact(
            id=self.id,
            title=self.title,
            observation_ids=self.observation_ids,
            model_id=self.model_id,
            gap_id=self.gap_id,
            hypothesis_ids=self.hypothesis_ids,
            prediction_ids=self.prediction_ids,
            experiment_id=self.experiment_id,
            outcome=self.outcome,
            epistemic_status=self.epistemic_status,
            reproduction_status=status,
        )
