"""Traceable discovery records from observation through reproduction."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any
from uuid import uuid4

from .durable import DurableEvent, SQLiteCognitiveJournal


@dataclass(frozen=True)
class DiscoveryArtifact:
    id: str = field(default_factory=lambda: "discovery-" + uuid4().hex[:16])
    title: str = ""
    problem: str = ""
    observations: tuple[str, ...] = ()
    current_explanation: str = ""
    explanatory_gap: str = ""
    hypotheses: tuple[str, ...] = ()
    derivation: tuple[str, ...] = ()
    predictions: tuple[str, ...] = ()
    experiment: str = ""
    outcomes: tuple[str, ...] = ()
    alternative_explanations: tuple[str, ...] = ()
    reproductions: tuple[str, ...] = ()
    epistemic_status: str = "candidate"
    novelty_status: str = "unassessed"

    def with_stage(self, **changes: Any) -> "DiscoveryArtifact":
        return replace(self, **changes)


class DurableDiscoveryArtifacts:
    """Persist discovery history as evidence, including unsuccessful paths."""

    def __init__(self, journal: SQLiteCognitiveJournal) -> None:
        self.journal = journal

    def record(self, artifact: DiscoveryArtifact) -> DurableEvent:
        return self.journal.append(DurableEvent(
            kind="discovery_artifact",
            source="discovery_lifecycle",
            payload={
                "id": artifact.id, "title": artifact.title, "problem": artifact.problem,
                "observations": list(artifact.observations), "current_explanation": artifact.current_explanation,
                "explanatory_gap": artifact.explanatory_gap, "hypotheses": list(artifact.hypotheses),
                "derivation": list(artifact.derivation), "predictions": list(artifact.predictions),
                "experiment": artifact.experiment, "outcomes": list(artifact.outcomes),
                "alternative_explanations": list(artifact.alternative_explanations),
                "reproductions": list(artifact.reproductions), "epistemic_status": artifact.epistemic_status,
                "novelty_status": artifact.novelty_status,
            },
        ))

    def all(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("discovery_artifact"))
