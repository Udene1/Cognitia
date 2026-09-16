"""Deterministic communicative cognition primitives.

This module deliberately contains no language model dependency.  Experiment 1
asks whether the same epistemic state can lead to different communicative acts
when the communicative objective changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class CommunicativeObjective(str, Enum):
    INFORM = "inform"
    INVESTIGATE = "investigate"
    DECISION_SUPPORT = "decision_support"
    TEACH = "teach"
    CLARIFY = "clarify"
    PARTIAL_RESULT = "partial_result"


class CommunicativeAct(str, Enum):
    REPORT_CURRENT_STATE = "report_current_state"
    PROPOSE_DISCRIMINATING_TEST = "propose_discriminating_test"
    SUPPORT_DECISION_UNDER_UNCERTAINTY = "support_decision_under_uncertainty"
    EXPLAIN_UNCERTAINTY = "explain_uncertainty"
    REQUEST_CLARIFICATION = "request_clarification"
    REPORT_LIMITATION_WITH_PARTIAL_RESULT = "report_limitation_with_partial_result"


@dataclass(frozen=True)
class HypothesisState:
    hypothesis_id: str
    description: str
    evidence_ids: tuple[str, ...] = ()
    evidence_strength: str = "none"


@dataclass(frozen=True)
class CognitiveCommunicationState:
    state_id: str
    question: str
    hypotheses: tuple[HypothesisState, ...]
    established_hypothesis_id: str | None
    uncertainty: tuple[str, ...]
    missing_discriminating_evidence: tuple[str, ...]
    capability_limits: tuple[str, ...] = ()

    @property
    def unresolved(self) -> bool:
        return self.established_hypothesis_id is None


@dataclass(frozen=True)
class InteractionContext:
    recipient: str | None = None
    objective: CommunicativeObjective | None = None


@dataclass(frozen=True)
class CommunicativeDecision:
    state_id: str
    objective: CommunicativeObjective
    recipient: str | None
    candidate_acts: tuple[CommunicativeAct, ...]
    selected_act: CommunicativeAct
    claim_ids: tuple[str, ...]
    omitted_claim_ids: tuple[str, ...]
    epistemic_status: tuple[tuple[str, str], ...]
    evidence_ids: tuple[str, ...]
    uncertainty: tuple[str, ...]
    requested_action: str | None
    verification_requirement: str | None


class EpistemicPreservationError(AssertionError):
    """Raised when communication upgrades or improperly weakens a claim."""


def select_communicative_act(
    state: CognitiveCommunicationState,
    context: InteractionContext,
) -> CommunicativeDecision:
    """Select an act from cognitive + epistemic + interaction state only.

    No prose generation occurs here.  The selector is intentionally explicit
    so that its behavior can be measured and later replaced by a learned
    mechanism if experiments justify one.
    """
    objective = context.objective
    if objective is None or context.recipient is None:
        return _decision(state, context, CommunicativeAct.REQUEST_CLARIFICATION, (), (), None)

    if objective is CommunicativeObjective.INFORM:
        selected = CommunicativeAct.REPORT_CURRENT_STATE
        claims = _supported_claims(state)
        omitted = tuple(h.hypothesis_id for h in state.hypotheses if h.hypothesis_id not in claims)
        return _decision(state, context, selected, claims, omitted, None)

    if objective is CommunicativeObjective.INVESTIGATE:
        selected = CommunicativeAct.PROPOSE_DISCRIMINATING_TEST
        claims = _supported_claims(state)
        action = _join(state.missing_discriminating_evidence) if state.missing_discriminating_evidence else "collect evidence that distinguishes the remaining hypotheses"
        return _decision(state, context, selected, claims, (), action)

    if objective is CommunicativeObjective.DECISION_SUPPORT:
        selected = CommunicativeAct.SUPPORT_DECISION_UNDER_UNCERTAINTY
        claims = _supported_claims(state)
        return _decision(state, context, selected, claims, (), "choose a reversible mitigation or investigation while preserving uncertainty")

    if objective is CommunicativeObjective.TEACH:
        selected = CommunicativeAct.EXPLAIN_UNCERTAINTY
        claims = tuple(h.hypothesis_id for h in state.hypotheses)
        return _decision(state, context, selected, claims, (), "explain why the evidence supports candidates without establishing a root cause")

    if objective is CommunicativeObjective.PARTIAL_RESULT:
        selected = CommunicativeAct.REPORT_LIMITATION_WITH_PARTIAL_RESULT
        claims = _supported_claims(state)
        return _decision(state, context, selected, claims, (), "verify the unresolved conclusion with the missing capability or evidence")

    return _decision(state, context, CommunicativeAct.REQUEST_CLARIFICATION, (), (), None)


def assert_epistemic_preservation(state: CognitiveCommunicationState, decision: CommunicativeDecision) -> None:
    """Verify that a communicative decision does not manufacture certainty."""
    known_ids = {h.hypothesis_id for h in state.hypotheses}
    for claim_id, status in decision.epistemic_status:
        if claim_id not in known_ids:
            raise EpistemicPreservationError(f"unknown claim {claim_id!r}")
        source = next(h for h in state.hypotheses if h.hypothesis_id == claim_id)
        if status == "established" and state.established_hypothesis_id != claim_id:
            raise EpistemicPreservationError(f"candidate {claim_id} was upgraded to established")
        if status == "supported_candidate" and source.evidence_strength not in {"strong", "moderate"}:
            raise EpistemicPreservationError(f"weak/unsupported claim {claim_id} was upgraded to supported candidate")
        if status == "unknown" and source.evidence_strength in {"strong", "moderate"}:
            raise EpistemicPreservationError(f"supported claim {claim_id} was unnecessarily weakened to unknown")


def _supported_claims(state: CognitiveCommunicationState) -> tuple[str, ...]:
    return tuple(h.hypothesis_id for h in state.hypotheses if h.evidence_strength in {"strong", "moderate"})


def _decision(
    state: CognitiveCommunicationState,
    context: InteractionContext,
    selected: CommunicativeAct,
    claims: Iterable[str],
    omitted: Iterable[str],
    requested_action: str | None,
) -> CommunicativeDecision:
    claims_tuple = tuple(claims)
    statuses = []
    evidence_ids = []
    for hypothesis in state.hypotheses:
        if hypothesis.hypothesis_id not in claims_tuple:
            continue
        status = "established" if state.established_hypothesis_id == hypothesis.hypothesis_id else (
            "supported_candidate" if hypothesis.evidence_strength in {"strong", "moderate"} else "candidate_uncertain"
        )
        statuses.append((hypothesis.hypothesis_id, status))
        evidence_ids.extend(hypothesis.evidence_ids)
    verification = "required" if state.unresolved or state.capability_limits else None
    return CommunicativeDecision(
        state_id=state.state_id,
        objective=context.objective or CommunicativeObjective.CLARIFY,
        recipient=context.recipient,
        candidate_acts=tuple(CommunicativeAct),
        selected_act=selected,
        claim_ids=claims_tuple,
        omitted_claim_ids=tuple(omitted),
        epistemic_status=tuple(statuses),
        evidence_ids=tuple(dict.fromkeys(evidence_ids)),
        uncertainty=state.uncertainty,
        requested_action=requested_action,
        verification_requirement=verification,
    )


def _join(values: Iterable[str]) -> str:
    cleaned = tuple(value.strip() for value in values if value.strip())
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    return "; ".join(cleaned)
