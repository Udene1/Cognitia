"""Discovery primitives for exploring explanatory gaps without pretending novelty is truth.

This module deliberately stops before "creative generation". It gives Cognitia a
structured way to represent what is unexplained, what the current model explains,
and what a candidate hypothesis would have to predict. Future hypothesis-space
search can operate on these structures without being coupled to an LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterable


class ExplanationStatus(StrEnum):
    EXPLAINED = "explained"
    PARTIAL = "partial"
    UNEXPLAINED = "unexplained"
    CONTRADICTED = "contradicted"


@dataclass(frozen=True)
class Observation:
    """An observation that a model may or may not explain."""

    id: str
    statement: str
    source: str = ""
    reliability: float = 1.0

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("observation id is required")
        if not self.statement.strip():
            raise ValueError("observation statement is required")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be between 0 and 1")


@dataclass(frozen=True)
class ExplanationAssessment:
    observation_id: str
    status: ExplanationStatus
    reason: str = ""


@dataclass(frozen=True)
class ExplanatoryGap:
    """A bounded description of what the current explanatory model cannot cover."""

    observation_ids: tuple[str, ...]
    missing_aspects: tuple[str, ...]
    competing_explanations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.observation_ids:
            raise ValueError("an explanatory gap needs observations")
        if not self.missing_aspects:
            raise ValueError("an explanatory gap needs a missing aspect")


@dataclass(frozen=True)
class HypothesisCandidate:
    """A candidate explanation; novelty and truth are intentionally separate."""

    id: str
    proposition: str
    derived_from_gap: tuple[str, ...]
    predictions: tuple[str, ...] = ()
    novelty_status: str = "unassessed"
    epistemic_status: str = "hypothesis"

    def __post_init__(self) -> None:
        if not self.id or not self.proposition.strip():
            raise ValueError("hypothesis id and proposition are required")
        if not self.derived_from_gap:
            raise ValueError("hypothesis must identify its explanatory gap")


@dataclass
class DiscoveryWorkspace:
    """Small explicit workspace for the unknown-space exploration loop."""

    observations: dict[str, Observation] = field(default_factory=dict)
    assessments: dict[str, ExplanationAssessment] = field(default_factory=dict)
    gaps: list[ExplanatoryGap] = field(default_factory=list)
    hypotheses: dict[str, HypothesisCandidate] = field(default_factory=dict)

    def add_observation(self, observation: Observation) -> None:
        self.observations[observation.id] = observation

    def assess(self, assessment: ExplanationAssessment) -> None:
        if assessment.observation_id not in self.observations:
            raise KeyError(f"unknown observation: {assessment.observation_id}")
        self.assessments[assessment.observation_id] = assessment

    def identify_gaps(self) -> tuple[ExplanatoryGap, ...]:
        unexplained = tuple(
            observation_id
            for observation_id, assessment in self.assessments.items()
            if assessment.status in {ExplanationStatus.UNEXPLAINED, ExplanationStatus.CONTRADICTED}
        )
        if not unexplained:
            return ()
        gap = ExplanatoryGap(
            observation_ids=unexplained,
            missing_aspects=tuple(
                self.assessments[item].reason or "current explanation is insufficient"
                for item in unexplained
            ),
        )
        if gap not in self.gaps:
            self.gaps.append(gap)
        return tuple(self.gaps)

    def register_hypothesis(self, hypothesis: HypothesisCandidate) -> None:
        known = set(self.observations)
        if not set(hypothesis.derived_from_gap).issubset(known):
            raise ValueError("hypothesis references observations outside the workspace")
        self.hypotheses[hypothesis.id] = hypothesis


def unresolved_observations(
    assessments: Iterable[ExplanationAssessment],
) -> tuple[str, ...]:
    """Return observations whose current explanatory status warrants investigation."""

    return tuple(
        item.observation_id
        for item in assessments
        if item.status in {ExplanationStatus.UNEXPLAINED, ExplanationStatus.CONTRADICTED}
    )
