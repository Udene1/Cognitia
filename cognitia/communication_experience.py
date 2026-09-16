"""Inspectable communication consequence and adaptation primitives.

This module deliberately implements a small deterministic policy learner so
Experiment 4 can measure whether observed communication consequences can alter
future act selection. It does not alter the underlying epistemic state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .communicative_cognition import (
    CommunicativeAct,
    CommunicativeDecision,
    EpistemicPreservationError,
)


@dataclass(frozen=True)
class CommunicationConsequence:
    decision_state_id: str
    selected_act: CommunicativeAct
    outcome: str
    signal: float
    observation: str


@dataclass(frozen=True)
class CommunicationExperience:
    experience_id: str
    decision_state_id: str
    objective: str
    recipient_role: str | None
    selected_act: CommunicativeAct
    outcome: str
    signal: float
    observation: str
    policy_revision: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class CommunicationPolicyState:
    scores: tuple[tuple[str, float], ...] = ()

    def score(self, act: CommunicativeAct) -> float:
        return dict(self.scores).get(act.value, 0.0)


class CommunicationPolicy:
    """A minimal stateful policy whose only input is recorded experience."""

    def __init__(self, state: CommunicationPolicyState | None = None) -> None:
        self._scores = dict(state.scores if state else ())
        self._experiences: list[CommunicationExperience] = []

    @property
    def state(self) -> CommunicationPolicyState:
        return CommunicationPolicyState(tuple(sorted(self._scores.items())))

    @property
    def experiences(self) -> tuple[CommunicationExperience, ...]:
        return tuple(self._experiences)

    def record(
        self,
        experience_id: str,
        decision: CommunicativeDecision,
        consequence: CommunicationConsequence,
    ) -> CommunicationExperience:
        if consequence.decision_state_id != decision.state_id:
            raise ValueError("consequence is not attached to the decision state")
        if consequence.selected_act is not decision.selected_act:
            raise ValueError("consequence is not attached to the selected act")
        before = dict(self._scores)
        self._scores[consequence.selected_act.value] = (
            self._scores.get(consequence.selected_act.value, 0.0) + consequence.signal
        )
        revision = tuple(
            sorted(
                (act, self._scores.get(act, 0.0) - before.get(act, 0.0))
                for act in self._scores
                if self._scores.get(act, 0.0) != before.get(act, 0.0)
            )
        )
        experience = CommunicationExperience(
            experience_id=experience_id,
            decision_state_id=decision.state_id,
            objective=decision.objective.value,
            recipient_role=decision.recipient_role.value if decision.recipient_role else None,
            selected_act=consequence.selected_act,
            outcome=consequence.outcome,
            signal=consequence.signal,
            observation=consequence.observation,
            policy_revision=revision,
        )
        self._experiences.append(experience)
        return experience

    def select(self, decision: CommunicativeDecision) -> CommunicativeDecision:
        """Apply learned preference only among the decision's existing acts."""
        candidates = decision.candidate_acts
        if not candidates:
            return decision
        selected = max(
            candidates,
            key=lambda act: (self._scores.get(act.value, 0.0), -candidates.index(act)),
        )
        if selected is decision.selected_act:
            return decision
        return CommunicativeDecision(
            state_id=decision.state_id,
            objective=decision.objective,
            recipient=decision.recipient,
            candidate_acts=decision.candidate_acts,
            selected_act=selected,
            claim_ids=decision.claim_ids,
            omitted_claim_ids=decision.omitted_claim_ids,
            epistemic_status=decision.epistemic_status,
            evidence_ids=decision.evidence_ids,
            uncertainty=decision.uncertainty,
            requested_action=decision.requested_action,
            verification_requirement=decision.verification_requirement,
            recipient_role=decision.recipient_role,
        )

    def assert_experience_driven_change(
        self,
        baseline: CommunicativeDecision,
        adapted: CommunicativeDecision,
    ) -> None:
        if not self._experiences:
            raise AssertionError("no communication experience was recorded")
        if adapted.selected_act is baseline.selected_act:
            raise AssertionError("recorded experience did not change the decision")
        if adapted.claim_ids != baseline.claim_ids:
            raise EpistemicPreservationError("adaptation changed claim identity")
        if adapted.evidence_ids != baseline.evidence_ids:
            raise EpistemicPreservationError("adaptation changed evidence identity")
        if adapted.uncertainty != baseline.uncertainty:
            raise EpistemicPreservationError("adaptation changed uncertainty")
        if adapted.epistemic_status != baseline.epistemic_status:
            raise EpistemicPreservationError("adaptation changed epistemic status")
        if adapted.verification_requirement != baseline.verification_requirement:
            raise EpistemicPreservationError("adaptation changed verification requirement")


def policy_state_delta(before: CommunicationPolicyState, after: CommunicationPolicyState) -> tuple[tuple[str, float], ...]:
    before_map = dict(before.scores)
    after_map = dict(after.scores)
    keys = set(before_map) | set(after_map)
    return tuple(sorted((key, after_map.get(key, 0.0) - before_map.get(key, 0.0)) for key in keys if after_map.get(key, 0.0) != before_map.get(key, 0.0)))
