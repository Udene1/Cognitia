"""Inspectable communication consequence and adaptation primitives.

This module deliberately implements a small deterministic policy learner so
communication experiments can measure whether observed consequences alter
future act selection and generalize across structurally related states.
It does not alter the underlying epistemic state.
"""
from __future__ import annotations

from dataclasses import dataclass

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
        """Return the legacy aggregate score for an act across contexts."""
        prefix = f"act|{act.value}|"
        return sum(value for key, value in self.scores if key.startswith(prefix))

    def score_for(self, objective: str, recipient_role: str | None, act: CommunicativeAct) -> float:
        return dict(self.scores).get(_policy_key(objective, recipient_role, act), 0.0)


class CommunicationPolicy:
    """A minimal stateful policy whose input is recorded experience.

    Learning is keyed by interaction structure (objective + recipient role),
    not by exact cognitive-state identity. This makes held-out state transfer
    observable while preventing one experience from globally changing every
    communication context.
    """

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
        key = _policy_key(decision.objective.value, decision.recipient_role.value if decision.recipient_role else None, consequence.selected_act)
        self._scores[key] = self._scores.get(key, 0.0) + consequence.signal
        revision = tuple(
            sorted(
                (key, self._scores.get(key, 0.0) - before.get(key, 0.0))
                for key in self._scores
                if self._scores.get(key, 0.0) != before.get(key, 0.0)
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
        """Apply learned preference only when experience exists for this context."""
        candidates = decision.candidate_acts
        if not candidates:
            return decision
        objective = decision.objective.value
        recipient_role = decision.recipient_role.value if decision.recipient_role else None
        context_scores = {
            act: self._scores.get(_policy_key(objective, recipient_role, act), 0.0)
            for act in candidates
        }
        if not any(_policy_key(objective, recipient_role, act) in self._scores for act in candidates):
            return decision
        selected = max(
            candidates,
            key=lambda act: (context_scores[act], -candidates.index(act)),
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


def _policy_key(objective: str, recipient_role: str | None, act: CommunicativeAct) -> str:
    return f"act|{act.value}|objective:{objective}|recipient:{recipient_role or 'unspecified'}"


def policy_state_delta(before: CommunicationPolicyState, after: CommunicationPolicyState) -> tuple[tuple[str, float], ...]:
    before_map = dict(before.scores)
    after_map = dict(after.scores)
    keys = set(before_map) | set(after_map)
    return tuple(sorted((key, after_map.get(key, 0.0) - before_map.get(key, 0.0)) for key in keys if after_map.get(key, 0.0) != before_map.get(key, 0.0)))
