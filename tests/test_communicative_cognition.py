from cognitia.communicative_cognition import (
    CommunicativeAct,
    CommunicativeObjective,
    CognitiveCommunicationState,
    EpistemicPreservationError,
    HypothesisState,
    InteractionContext,
    RecipientRole,
    assert_epistemic_preservation,
    select_communicative_act,
)


def unresolved_failure_state() -> CognitiveCommunicationState:
    return CognitiveCommunicationState(
        state_id="roman-empire-controlled-1",
        question="Why did system X fail?",
        hypotheses=(
            HypothesisState("H1", "resource exhaustion", ("E1",), "strong"),
            HypothesisState("H2", "dependency failure", ("E2",), "weak"),
            HypothesisState("H3", "configuration error", (), "none"),
        ),
        established_hypothesis_id=None,
        uncertainty=("no root cause is established", "H1 and H2 remain discriminable candidates"),
        missing_discriminating_evidence=("observation distinguishing resource exhaustion from dependency failure",),
    )


def test_same_cognitive_state_changes_act_with_objective():
    state = unresolved_failure_state()
    recipient = "operator"
    decisions = {
        objective: select_communicative_act(state, InteractionContext(recipient, objective))
        for objective in (
            CommunicativeObjective.INFORM,
            CommunicativeObjective.INVESTIGATE,
            CommunicativeObjective.DECISION_SUPPORT,
            CommunicativeObjective.TEACH,
        )
    }

    assert decisions[CommunicativeObjective.INFORM].selected_act is CommunicativeAct.REPORT_CURRENT_STATE
    assert decisions[CommunicativeObjective.INVESTIGATE].selected_act is CommunicativeAct.PROPOSE_DISCRIMINATING_TEST
    assert decisions[CommunicativeObjective.DECISION_SUPPORT].selected_act is CommunicativeAct.SUPPORT_DECISION_UNDER_UNCERTAINTY
    assert decisions[CommunicativeObjective.TEACH].selected_act is CommunicativeAct.EXPLAIN_UNCERTAINTY
    assert len({decision.selected_act for decision in decisions.values()}) == 4


def test_objective_changes_act_not_epistemic_warrant():
    state = unresolved_failure_state()
    for objective in CommunicativeObjective:
        decision = select_communicative_act(state, InteractionContext("operator", objective))
        assert all(status != "established" for _, status in decision.epistemic_status)
        assert_epistemic_preservation(state, decision)


def test_ambiguous_interaction_requests_clarification():
    state = unresolved_failure_state()
    decision = select_communicative_act(state, InteractionContext(recipient=None, objective=None))
    assert decision.selected_act is CommunicativeAct.REQUEST_CLARIFICATION
    assert decision.claim_ids == ()


def test_insufficient_capability_still_communicates_partial_result():
    state = CognitiveCommunicationState(
        state_id="capability-limit-1",
        question="Can the current evidence establish the root cause?",
        hypotheses=(HypothesisState("H1", "resource exhaustion", ("E1",), "strong"),),
        established_hypothesis_id=None,
        uncertainty=("root cause not established",),
        missing_discriminating_evidence=("runtime trace",),
        capability_limits=("cannot inspect runtime trace",),
    )
    decision = select_communicative_act(state, InteractionContext("operator", CommunicativeObjective.PARTIAL_RESULT))
    assert decision.selected_act is CommunicativeAct.REPORT_LIMITATION_WITH_PARTIAL_RESULT
    assert decision.verification_requirement == "required"
    assert_epistemic_preservation(state, decision)


def test_preservation_rejects_candidate_to_fact_upgrade():
    state = unresolved_failure_state()
    decision = select_communicative_act(state, InteractionContext("operator", CommunicativeObjective.INFORM))
    bad = decision.__class__(
        **{**decision.__dict__, "epistemic_status": (("H1", "established"),)}
    )
    try:
        assert_epistemic_preservation(state, bad)
    except EpistemicPreservationError:
        return
    raise AssertionError("candidate-to-fact upgrade was not rejected")


def test_same_state_and_objective_changes_act_with_recipient_role():
    state = unresolved_failure_state()
    objective = CommunicativeObjective.INFORM
    decisions = {
        role: select_communicative_act(
            state,
            InteractionContext("recipient", objective, recipient_role=role),
        )
        for role in RecipientRole
    }

    assert decisions[RecipientRole.OPERATOR].selected_act is CommunicativeAct.REPORT_CURRENT_STATE
    assert decisions[RecipientRole.DECISION_MAKER].selected_act is CommunicativeAct.SUPPORT_DECISION_UNDER_UNCERTAINTY
    assert decisions[RecipientRole.LEARNER].selected_act is CommunicativeAct.EXPLAIN_UNCERTAINTY
    assert len({decision.selected_act for decision in decisions.values()}) == 3


def test_recipient_adaptation_preserves_epistemic_warrant():
    state = unresolved_failure_state()
    objective = CommunicativeObjective.INFORM
    for role in RecipientRole:
        decision = select_communicative_act(
            state,
            InteractionContext("recipient", objective, recipient_role=role),
        )
        assert all(status != "established" for _, status in decision.epistemic_status)
        assert_epistemic_preservation(state, decision)
        assert decision.state_id == state.state_id
        assert decision.objective is objective


def test_recipient_context_is_recorded_without_changing_cognitive_state():
    state = unresolved_failure_state()
    decision = select_communicative_act(
        state,
        InteractionContext(
            "decision-maker",
            CommunicativeObjective.INFORM,
            recipient_role=RecipientRole.DECISION_MAKER,
            interaction_constraints=("brief", "action-oriented"),
        ),
    )
    assert decision.recipient_role is RecipientRole.DECISION_MAKER
    assert decision.state_id == state.state_id
    assert decision.uncertainty == state.uncertainty
    assert decision.verification_requirement == "required"
