"""Durable, inspectable records for research trajectory experiments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .environment import EnvironmentObservation
from .open_research import OpenResearchRound


@dataclass(frozen=True)
class ResearchTrajectoryStep:
    """One observed research action and the state it produced."""

    sequence: int
    action_id: str
    parent_action_id: str | None
    purpose: str
    objective: str
    decision_rationale: str
    expected_information_gain: float
    information_need: str | None
    information_need_source_claim_ids: tuple[str, ...]
    information_need_source_document_ids: tuple[str, ...]
    search_observation_ids: tuple[str, ...]
    document_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    cluster_count: int
    conflict_count: int
    source_origins: tuple[str, ...]

    @property
    def unresolved_information_needs(self) -> tuple[str, ...]:
        return (self.information_need,) if self.information_need else ()


@dataclass(frozen=True)
class ResearchTrajectory:
    """A reconstruction of one bounded research episode."""

    question: str
    steps: tuple[ResearchTrajectoryStep, ...]
    final_unresolved_information_needs: tuple[str, ...]

    @property
    def action_count(self) -> int:
        return len(self.steps)

    @property
    def observed_document_count(self) -> int:
        return sum(len(step.document_ids) for step in self.steps)

    @property
    def observed_claim_count(self) -> int:
        return sum(len(step.claim_ids) for step in self.steps)

    @property
    def adaptive_transition_count(self) -> int:
        return sum(step.parent_action_id is not None for step in self.steps)

    def step(self, sequence: int) -> ResearchTrajectoryStep:
        return self.steps[sequence]


def reconstruct_trajectory(
    question: str,
    rounds: Iterable[OpenResearchRound],
    *,
    final_unresolved: Iterable[str] = (),
) -> ResearchTrajectory:
    """Reconstruct the observable research path without inferring causality."""
    steps: list[ResearchTrajectoryStep] = []

    for sequence, research_round in enumerate(rounds):
        documents = tuple(doc.id for doc in research_round.documents)
        claims = tuple(claim.id for claim in research_round.claims)
        conflicts = tuple(cluster for cluster in research_round.clusters if cluster.conflict)

        steps.append(
            ResearchTrajectoryStep(
                sequence=sequence,
                action_id=research_round.action_id,
                parent_action_id=research_round.parent_action_id,
                purpose=research_round.action.purpose,
                objective=research_round.action.query.objective,
                decision_rationale=research_round.decision_rationale,
                expected_information_gain=research_round.expected_information_gain,
                information_need=research_round.information_need,
                information_need_source_claim_ids=research_round.information_need_source_claim_ids,
                information_need_source_document_ids=research_round.information_need_source_document_ids,
                search_observation_ids=tuple(obs.id for obs in research_round.search_observations),
                document_ids=documents,
                claim_ids=claims,
                cluster_count=len(research_round.clusters),
                conflict_count=len(conflicts),
                source_origins=_source_origins(research_round.documents),
            )
        )

    return ResearchTrajectory(
        question=question,
        steps=tuple(steps),
        final_unresolved_information_needs=tuple(final_unresolved),
    )


def _source_origins(documents: Iterable[EnvironmentObservation]) -> tuple[str, ...]:
    origins: list[str] = []
    for document in documents:
        source = getattr(document, "source", None)
        origin = getattr(source, "origin", None) or getattr(source, "name", None) or str(source or "unknown")
        if origin not in origins:
            origins.append(origin)
    return tuple(origins)
