"""Causal experience records for Cognitia's cross-capability research loop.

This module is deliberately domain-neutral and deterministic. It does not
learn a policy and it does not infer cognition. It makes the state -> action
-> consequence -> updated-state boundary explicit enough to measure whether
experience can later affect behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence


class EpistemicOutcome(str, Enum):
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    UNRESOLVED = "unresolved"
    PARTIAL = "partial"


@dataclass(frozen=True)
class CognitiveState:
    """State visible immediately before an action is selected."""

    problem: str
    evidence_ids: tuple[str, ...] = ()
    knowledge_ids: tuple[str, ...] = ()
    hypothesis_ids: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    goal: str | None = None

    def __post_init__(self) -> None:
        if not self.problem.strip():
            raise ValueError("problem is required")


@dataclass(frozen=True)
class ExpectedConsequence:
    description: str
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObservedConsequence:
    description: str
    outcome: EpistemicOutcome
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Experience:
    """One auditable interaction between cognitive state, action and world."""

    experience_id: str
    prior_state: CognitiveState
    action: str
    rationale: str
    expected: ExpectedConsequence
    observed: ObservedConsequence
    state_update: CognitiveState
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (("experience_id", self.experience_id), ("action", self.action)):
            if not value.strip():
                raise ValueError(f"{name} is required")
        if not self.rationale.strip():
            raise ValueError("rationale is required")

    @property
    def discrepancy(self) -> bool:
        return self.expected.description.strip().lower() != self.observed.description.strip().lower()


class ExperienceLedger:
    """Append-only experience store with deterministic retrieval predicates."""

    def __init__(self, experiences: Sequence[Experience] = ()) -> None:
        self._experiences = list(experiences)
        self._ids = {item.experience_id for item in self._experiences}
        if len(self._ids) != len(self._experiences):
            raise ValueError("experience IDs must be unique")

    def record(self, experience: Experience) -> Experience:
        if experience.experience_id in self._ids:
            raise ValueError(f"experience already recorded: {experience.experience_id}")
        self._experiences.append(experience)
        self._ids.add(experience.experience_id)
        return experience

    def all(self) -> tuple[Experience, ...]:
        return tuple(self._experiences)

    def by_outcome(self, outcome: EpistemicOutcome) -> tuple[Experience, ...]:
        return tuple(item for item in self._experiences if item.observed.outcome is outcome)

    def with_action(self, action: str) -> tuple[Experience, ...]:
        return tuple(item for item in self._experiences if item.action == action)

    def relevant_to(self, *, evidence_ids: Sequence[str] = (), hypothesis_ids: Sequence[str] = ()) -> tuple[Experience, ...]:
        evidence = set(evidence_ids)
        hypotheses = set(hypothesis_ids)
        return tuple(
            item for item in self._experiences
            if evidence.intersection(item.prior_state.evidence_ids)
            or evidence.intersection(item.observed.evidence_ids)
            or hypotheses.intersection(item.prior_state.hypothesis_ids)
        )


def state_fingerprint(state: CognitiveState) -> tuple[str, tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], str | None]:
    """Stable structural representation used by experiments, not semantic magic."""
    return (
        state.problem.strip().lower(),
        tuple(sorted(state.evidence_ids)),
        tuple(sorted(state.knowledge_ids)),
        tuple(sorted(state.hypothesis_ids)),
        tuple(sorted(state.uncertainty)),
        state.goal.strip().lower() if state.goal else None,
    )


def summarize_experience(experience: Experience) -> Mapping[str, object]:
    """Produce a lossless-enough structured research record for inspection."""
    return {
        "experience_id": experience.experience_id,
        "prior_state": state_fingerprint(experience.prior_state),
        "action": experience.action,
        "rationale": experience.rationale,
        "expected": {
            "description": experience.expected.description,
            "evidence_ids": list(experience.expected.evidence_ids),
        },
        "observed": {
            "description": experience.observed.description,
            "outcome": experience.observed.outcome.value,
            "evidence_ids": list(experience.observed.evidence_ids),
        },
        "discrepancy": experience.discrepancy,
        "state_update": state_fingerprint(experience.state_update),
        "provenance": list(experience.provenance),
    }
