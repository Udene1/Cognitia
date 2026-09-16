"""Deterministic communicative cognition primitives.

Communication is represented as structured action selection followed by an
explicit representation projection. No language model is used for either step.
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

class RecipientRole(str, Enum):
    OPERATOR = "operator"
    DECISION_MAKER = "decision_maker"
    LEARNER = "learner"

class CommunicationRepresentation(str, Enum):
    STRUCTURED = "structured"
    CONCISE = "concise"
    EXPLANATORY = "explanatory"

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
    recipient_role: RecipientRole | None = None
    interaction_constraints: tuple[str, ...] = ()

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
    recipient_role: RecipientRole | None = None

@dataclass(frozen=True)
class CommunicationProjection:
    representation: CommunicationRepresentation
    selected_act: CommunicativeAct
    claim_ids: tuple[str, ...]
    omitted_claim_ids: tuple[str, ...]
    epistemic_status: tuple[tuple[str, str], ...]
    evidence_ids: tuple[str, ...]
    uncertainty: tuple[str, ...]
    verification_requirement: str | None
    payload: tuple[str, ...]

class EpistemicPreservationError(AssertionError):
    """Raised when communication upgrades or improperly weakens a claim."""

def select_communicative_act(state: CognitiveCommunicationState, context: InteractionContext) -> CommunicativeDecision:
    objective = context.objective
    if objective is None or context.recipient is None:
        return _decision(state, context, CommunicativeAct.REQUEST_CLARIFICATION, (), (), None)
    if objective is CommunicativeObjective.INFORM:
        selected = _inform_act_for_recipient(context)
        claims = _supported_claims(state)
        omitted = tuple(h.hypothesis_id for h in state.hypotheses if h.hypothesis_id not in claims)
        return _decision(state, context, selected, claims, omitted, _recipient_action(selected))
    if objective is CommunicativeObjective.INVESTIGATE:
        selected = CommunicativeAct.PROPOSE_DISCRIMINATING_TEST
        claims = _supported_claims(state)
        action = _join(state.missing_discriminating_evidence) if state.missing_discriminating_evidence else "collect evidence that distinguishes the remaining hypotheses"
        return _decision(state, context, selected, claims, (), action)
    if objective is CommunicativeObjective.DECISION_SUPPORT:
        return _decision(state, context, CommunicativeAct.SUPPORT_DECISION_UNDER_UNCERTAINTY, _supported_claims(state), (), "choose a reversible mitigation or investigation while preserving uncertainty")
    if objective is CommunicativeObjective.TEACH:
        return _decision(state, context, CommunicativeAct.EXPLAIN_UNCERTAINTY, tuple(h.hypothesis_id for h in state.hypotheses), (), "explain why the evidence supports candidates without establishing a root cause")
    if objective is CommunicativeObjective.PARTIAL_RESULT:
        return _decision(state, context, CommunicativeAct.REPORT_LIMITATION_WITH_PARTIAL_RESULT, _supported_claims(state), (), "verify the unresolved conclusion with the missing capability or evidence")
    return _decision(state, context, CommunicativeAct.REQUEST_CLARIFICATION, (), (), None)

def project_communication(decision: CommunicativeDecision, representation: CommunicationRepresentation) -> CommunicationProjection:
    """Project one act into explicit surfaces without changing its commitments."""
    common = (f"act:{decision.selected_act.value}", f"claims:{','.join(decision.claim_ids)}", f"evidence:{','.join(decision.evidence_ids)}", f"uncertainty:{';'.join(decision.uncertainty)}", f"verification:{decision.verification_requirement or 'none'}")
    if representation is CommunicationRepresentation.STRUCTURED:
        payload = common
    elif representation is CommunicationRepresentation.CONCISE:
        payload = (common[0], common[1], common[3], common[4])
    else:
        payload = common + (f"not_established:{','.join(decision.omitted_claim_ids)}",)
    return CommunicationProjection(representation, decision.selected_act, decision.claim_ids, decision.omitted_claim_ids, decision.epistemic_status, decision.evidence_ids, decision.uncertainty, decision.verification_requirement, payload)

def assert_epistemic_preservation(state: CognitiveCommunicationState, decision: CommunicativeDecision) -> None:
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

def assert_projection_preservation(decision: CommunicativeDecision, projection: CommunicationProjection) -> None:
    pairs = (("selected_act", decision.selected_act, projection.selected_act), ("claim_ids", decision.claim_ids, projection.claim_ids), ("omitted_claim_ids", decision.omitted_claim_ids, projection.omitted_claim_ids), ("epistemic_status", decision.epistemic_status, projection.epistemic_status), ("evidence_ids", decision.evidence_ids, projection.evidence_ids), ("uncertainty", decision.uncertainty, projection.uncertainty), ("verification_requirement", decision.verification_requirement, projection.verification_requirement))
    for name, expected, observed in pairs:
        if expected != observed:
            raise EpistemicPreservationError(f"representation changed {name}")

def _inform_act_for_recipient(context: InteractionContext) -> CommunicativeAct:
    if context.recipient_role is RecipientRole.DECISION_MAKER:
        return CommunicativeAct.SUPPORT_DECISION_UNDER_UNCERTAINTY
    if context.recipient_role is RecipientRole.LEARNER:
        return CommunicativeAct.EXPLAIN_UNCERTAINTY
    return CommunicativeAct.REPORT_CURRENT_STATE

def _recipient_action(act: CommunicativeAct) -> str | None:
    if act is CommunicativeAct.REPORT_CURRENT_STATE:
        return "review the current evidence and unresolved state"
    if act is CommunicativeAct.SUPPORT_DECISION_UNDER_UNCERTAINTY:
        return "choose a reversible mitigation or investigation while preserving uncertainty"
    if act is CommunicativeAct.EXPLAIN_UNCERTAINTY:
        return "explain why the evidence supports candidates without establishing a root cause"
    return None

def _supported_claims(state: CognitiveCommunicationState) -> tuple[str, ...]:
    return tuple(h.hypothesis_id for h in state.hypotheses if h.evidence_strength in {"strong", "moderate"})

def _decision(state: CognitiveCommunicationState, context: InteractionContext, selected: CommunicativeAct, claims: Iterable[str], omitted: Iterable[str], requested_action: str | None) -> CommunicativeDecision:
    claims_tuple = tuple(claims)
    statuses = []
    evidence_ids = []
    for hypothesis in state.hypotheses:
        if hypothesis.hypothesis_id not in claims_tuple:
            continue
        status = "established" if state.established_hypothesis_id == hypothesis.hypothesis_id else ("supported_candidate" if hypothesis.evidence_strength in {"strong", "moderate"} else "candidate_uncertain")
        statuses.append((hypothesis.hypothesis_id, status))
        evidence_ids.extend(hypothesis.evidence_ids)
    verification = "required" if state.unresolved or state.capability_limits else None
    return CommunicativeDecision(state.state_id, context.objective or CommunicativeObjective.CLARIFY, context.recipient, tuple(CommunicativeAct), selected, claims_tuple, tuple(omitted), tuple(statuses), tuple(dict.fromkeys(evidence_ids)), state.uncertainty, requested_action, verification, context.recipient_role)

def _join(values: Iterable[str]) -> str:
    cleaned = tuple(value.strip() for value in values if value.strip())
    return "" if not cleaned else cleaned[0] if len(cleaned) == 1 else "; ".join(cleaned)
