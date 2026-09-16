from cognitia.communication_experience import CommunicationConsequence, CommunicationPolicy
from cognitia.communicative_cognition import (
    CommunicativeAct,
    CommunicativeObjective,
    CognitiveCommunicationState,
    CommunicationRepresentation,
    HypothesisState,
    InteractionContext,
    RecipientRole,
    assert_observable_evidence_recovery,
    assert_projection_preservation,
    project_communication,
    select_communicative_act,
)


def _training_state() -> CognitiveCommunicationState:
    return CognitiveCommunicationState(
        state_id="generalization-train",
        question="Why did service A fail?",
        hypotheses=(
            HypothesisState("A1", "resource exhaustion", ("EA1",), "strong"),
            HypothesisState("A2", "dependency failure", ("EA2",), "weak"),
        ),
        established_hypothesis_id=None,
        uncertainty=("service A root cause remains unresolved",),
        missing_discriminating_evidence=("trace separating A1 from A2",),
    )


def _held_out_state() -> CognitiveCommunicationState:
    return CognitiveCommunicationState(
        state_id="generalization-held-out",
        question="Why did service B fail?",
        hypotheses=(
            HypothesisState("B1", "database saturation", ("EB1",), "strong"),
            HypothesisState("B2", "network dependency failure", ("EB2",), "weak"),
        ),
        established_hypothesis_id=None,
        uncertainty=("service B root cause remains unresolved",),
        missing_discriminating_evidence=("trace separating B1 from B2",),
    )


def _decision(state, objective=CommunicativeObjective.INFORM, role=RecipientRole.OPERATOR):
    return select_communicative_act(
        state,
        InteractionContext("operator", objective, recipient_role=role),
    )


def test_experience_transfers_to_structurally_related_held_out_state():
    training = _decision(_training_state())
    held_out = _decision(_held_out_state())
    assert training.selected_act is CommunicativeAct.REPORT_CURRENT_STATE
    assert held_out.selected_act is CommunicativeAct.REPORT_CURRENT_STATE
    assert training.state_id != held_out.state_id
    assert training.claim_ids != held_out.claim_ids

    policy = CommunicationPolicy()
    policy.record(
        "train-report-stalled",
        training,
        CommunicationConsequence(
            training.state_id,
            training.selected_act,
            "stalled",
            -1.0,
            "state report did not make the unresolved distinction actionable",
        ),
    )
    policy.record(
        "train-explain-useful",
        training.__class__(**{**training.__dict__, "selected_act": CommunicativeAct.EXPLAIN_UNCERTAINTY}),
        CommunicationConsequence(
            training.state_id,
            CommunicativeAct.EXPLAIN_UNCERTAINTY,
            "useful",
            1.0,
            "explanation made the unresolved distinction actionable",
        ),
    )

    adapted = policy.select(held_out)
    assert adapted.state_id == held_out.state_id
    assert adapted.selected_act is CommunicativeAct.EXPLAIN_UNCERTAINTY
    assert adapted.claim_ids == held_out.claim_ids
    assert adapted.evidence_ids == held_out.evidence_ids
    assert adapted.uncertainty == held_out.uncertainty
    assert adapted.epistemic_status == held_out.epistemic_status
    assert adapted.verification_requirement == held_out.verification_requirement


def test_experience_does_not_transfer_across_unrelated_objective():
    training = _decision(_training_state(), CommunicativeObjective.INFORM)
    unrelated = _decision(_held_out_state(), CommunicativeObjective.INVESTIGATE)
    assert unrelated.selected_act is CommunicativeAct.PROPOSE_DISCRIMINATING_TEST

    policy = CommunicationPolicy()
    policy.record(
        "train-report-stalled",
        training,
        CommunicationConsequence(training.state_id, training.selected_act, "stalled", -1.0, "report was not actionable"),
    )
    policy.record(
        "train-explain-useful",
        training.__class__(**{**training.__dict__, "selected_act": CommunicativeAct.EXPLAIN_UNCERTAINTY}),
        CommunicationConsequence(training.state_id, CommunicativeAct.EXPLAIN_UNCERTAINTY, "useful", 1.0, "explanation was actionable"),
    )

    adapted = policy.select(unrelated)
    assert adapted.selected_act is CommunicativeAct.PROPOSE_DISCRIMINATING_TEST


def test_held_out_transfer_survives_representation_shift():
    training = _decision(_training_state())
    held_out = _decision(_held_out_state())
    policy = CommunicationPolicy()
    policy.record(
        "train-report-stalled",
        training,
        CommunicationConsequence(training.state_id, training.selected_act, "stalled", -1.0, "report stalled"),
    )
    policy.record(
        "train-explain-useful",
        training.__class__(**{**training.__dict__, "selected_act": CommunicativeAct.EXPLAIN_UNCERTAINTY}),
        CommunicationConsequence(training.state_id, CommunicativeAct.EXPLAIN_UNCERTAINTY, "useful", 1.0, "explanation helped"),
    )

    adapted = policy.select(held_out)
    projection = project_communication(adapted, CommunicationRepresentation.COMPACT_REFERENCED)
    assert adapted.selected_act is CommunicativeAct.EXPLAIN_UNCERTAINTY
    assert_projection_preservation(adapted, projection)
    assert_observable_evidence_recovery(adapted, projection)
    assert "act:explain_uncertainty" in projection.payload
    assert "evidence_ref:EB1" in projection.payload


def test_fresh_policy_is_held_out_baseline_control():
    held_out = _decision(_held_out_state())
    adapted = CommunicationPolicy().select(held_out)
    assert adapted.selected_act is CommunicativeAct.REPORT_CURRENT_STATE
