"""Durable, inspectable records for research trajectory experiments.

This module deliberately records research behavior without changing how research
is selected. The first experiment is observability: we want to reconstruct what
Cognitia observed, what information need remained, and why an action was taken
before introducing adaptive planning.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .environment import EnvironmentObservation
from .open_research import ClaimCluster, OpenResearchRound


@dataclass(frozen=True)
class ResearchTrajectoryStep:
    """One observed research action and the state it produced."""

    sequence: int
    action_id: str
    purpose: str
    objective: str
    decision_rationale: str
    expected_information_gain: float
    search_observation_ids: tuple[str, ...]
    document_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    cluster_count: int
    conflict_count: int
    unresolved_information_needs: tuple[str, ...]
    source_origins: tuple[str, ...]


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

    def step(self, sequence: int) -> ResearchTrajectoryStep:
        return self.steps[sequence]


def reconstruct_trajectory(
    question: str,
    rounds: Iterable[OpenResearchRound],
    *,
    final_unresolved: Iterable[str] = (),
) -> ResearchTrajectory:
    """Convert an existing research result into an inspectable trajectory.

    This is intentionally observational. It does not infer that a later action
    was caused by an earlier observation; it records the evidence needed to test
    that claim in a later adaptive experiment.
    """
    steps: list[ResearchTrajectoryStep] = []
    previous_documents: set[str] = set()
    previous_claims: set[str] = set()

    for sequence, research_round in enumerate(rounds):
        documents = tuple(doc.id for doc in research_round.documents)
        claims = tuple(claim.id for claim in research_round.claims)
        conflicts = tuple(cluster for cluster in research_round.clusters if cluster.conflict)
        source_origins = _source_origins(research_round.documents)

        # The current implementation does not yet expose Cognitia's internal
        # information-need state. Keep this empty rather than inventing a causal
        # explanation from the query or result.
        information_needs: tuple[str, ...] = ()

        steps.append(
            ResearchTrajectoryStep(
                sequence=sequence,
                action_id=_action_id(research_round),
                purpose=research_round.action.purpose,
                objective=research_round.action.query.objective,
                decision_rationale=research_round.decision_rationale,
                expected_information_gain=research_round.expected_information_gain,
                search_observation_ids=tuple(obs.id for obs in research_round.search_observations),
                document_ids=documents,
                claim_ids=claims,
                cluster_count=len(research_round.clusters),
                conflict_count=len(conflicts),
                unresolved_information_needs=information_needs,
                source_origins=source_origins,
            )
        )
        previous_documents.update(documents)
        previous_claims.update(claims)

    return ResearchTrajectory(
        question=question,
        steps=tuple(steps),
        final_unresolved_information_needs=tuple(final_unresolved),
    )


def _action_id(research_round: OpenResearchRound) -> str:
    query = research_round.action.query.objective.strip().lower()
    return f"{research_round.action.purpose}:{query}"


def _source_origins(documents: Iterable[EnvironmentObservation]) -> tuple[str, ...]:
    origins: list[str] = []
    for document in documents:
        source = getattr(document, "source", None)
        origin = getattr(source, "origin", None) or getattr(source, "name", None) or str(source or "unknown")
        if origin not in origins:
            origins.append(origin)
    return tuple(origins)
