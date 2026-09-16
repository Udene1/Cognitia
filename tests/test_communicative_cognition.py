from cognitia.communicative_cognition import (
    CommunicativeAct, CommunicativeObjective, CognitiveCommunicationState,
    CommunicationRepresentation, EpistemicPreservationError, HypothesisState,
    InteractionContext, RecipientRole, assert_epistemic_preservation,
    assert_observable_evidence_recovery, assert_projection_preservation,
    project_communication, select_communicative_act,
)


def unresolved_failure_state() -> CognitiveCommunicationState:
    return CognitiveCommunicationState(
        state_id="roman-empire-controlled-1", question="Why did system X fail?",
        hypotheses=(HypothesisState("H1", "resource exhaustion", ("E1",), "strong"), HypothesisState("H2", "dependency failure", ("E2",), "weak"), HypothesisState("H3", "configuration error", (), "none")),
        established_hypothesis_id=None,
        uncertainty=("no root cause is established", "H1 and H2 remain discriminable candidates"),
        missing_discriminating_evidence=("observation distinguishing resource exhaustion from dependency failure",),
    )


def test_same_cognitive_state_changes_act_with_objective():
    state = unresolved_failure_state(); recipient = "operator"
    decisions = {objective: select_communicative_act(state, InteractionContext(recipient, objective)) for objective in (CommunicativeObjective.INFORM, CommunicativeObjective.INVESTIGATE, CommunicativeObjective.DECISION_SUPPORT, CommunicativeObjective.TEACH)}
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
    decision = select_communicative_act(unresolved_failure_state(), InteractionContext())
    assert decision.selected_act is CommunicativeAct.REQUEST_CLARIFICATION
    assert decision.claim_ids == ()


def test_insufficient_capability_still_communicates_partial_result():
    state = CognitiveCommunicationState("capability-limit-1", "Can evidence establish root cause?", (HypothesisState("H1", "resource exhaustion", ("E1",), "strong"),), None, ("root cause not established",), ("runtime trace",), ("cannot inspect runtime trace",))
    decision = select_communicative_act(state, InteractionContext("operator", CommunicativeObjective.PARTIAL_RESULT))
    assert decision.selected_act is CommunicativeAct.REPORT_LIMITATION_WITH_PARTIAL_RESULT
    assert decision.verification_requirement == "required"
    assert_epistemic_preservation(state, decision)


def test_preservation_rejects_candidate_to_fact_upgrade():
    state = unresolved_failure_state(); decision = select_communicative_act(state, InteractionContext("operator", CommunicativeObjective.INFORM))
    bad = decision.__class__(**{**decision.__dict__, "epistemic_status": (("H1", "established"),)})
    try: assert_epistemic_preservation(state, bad)
    except EpistemicPreservationError: return
    raise AssertionError("candidate-to-fact upgrade was not rejected")


def test_same_state_and_objective_changes_act_with_recipient_role():
    state = unresolved_failure_state(); objective = CommunicativeObjective.INFORM
    decisions = {role: select_communicative_act(state, InteractionContext("recipient", objective, recipient_role=role)) for role in RecipientRole}
    assert decisions[RecipientRole.OPERATOR].selected_act is CommunicativeAct.REPORT_CURRENT_STATE
    assert decisions[RecipientRole.DECISION_MAKER].selected_act is CommunicativeAct.SUPPORT_DECISION_UNDER_UNCERTAINTY
    assert decisions[RecipientRole.LEARNER].selected_act is CommunicativeAct.EXPLAIN_UNCERTAINTY
    assert len({decision.selected_act for decision in decisions.values()}) == 3


def test_recipient_adaptation_preserves_epistemic_warrant():
    state = unresolved_failure_state(); objective = CommunicativeObjective.INFORM
    for role in RecipientRole:
        decision = select_communicative_act(state, InteractionContext("recipient", objective, recipient_role=role))
        assert all(status != "established" for _, status in decision.epistemic_status)
        assert_epistemic_preservation(state, decision)
        assert decision.state_id == state.state_id
        assert decision.objective is objective


def test_recipient_context_is_recorded_without_changing_cognitive_state():
    state = unresolved_failure_state()
    decision = select_communicative_act(state, InteractionContext("decision-maker", CommunicativeObjective.INFORM, recipient_role=RecipientRole.DECISION_MAKER, interaction_constraints=("brief", "action-oriented")))
    assert decision.recipient_role is RecipientRole.DECISION_MAKER
    assert decision.state_id == state.state_id
    assert decision.uncertainty == state.uncertainty
    assert decision.verification_requirement == "required"


def test_surface_representations_preserve_the_same_communication_contract():
    state = unresolved_failure_state()
    decision = select_communicative_act(state, InteractionContext("operator", CommunicativeObjective.INFORM, recipient_role=RecipientRole.OPERATOR))
    representations = (CommunicationRepresentation.STRUCTURED, CommunicationRepresentation.CONCISE, CommunicationRepresentation.EXPLANATORY)
    projections = [project_communication(decision, representation) for representation in representations]
    assert {projection.selected_act for projection in projections} == {decision.selected_act}
    assert {projection.representation for projection in projections} == set(representations)
    for projection in projections:
        assert_projection_preservation(decision, projection)
        assert projection.verification_requirement == "required"
        assert "act:report_current_state" in projection.payload
        assert "claims:H1" in projection.payload
        assert "evidence:E1" in projection.payload


def test_surface_projection_does_not_invent_or_remove_epistemic_status():
    state = unresolved_failure_state()
    decision = select_communicative_act(state, InteractionContext("learner", CommunicativeObjective.INFORM, recipient_role=RecipientRole.LEARNER))
    projection = project_communication(decision, CommunicationRepresentation.EXPLANATORY)
    assert projection.epistemic_status == decision.epistemic_status
    assert all(status != "established" for _, status in projection.epistemic_status)
    assert_projection_preservation(decision, projection)


def test_boundary_experiment_accepts_losslessly_referenced_evidence():
    state = unresolved_failure_state()
    decision = select_communicative_act(state, InteractionContext("operator", CommunicativeObjective.INFORM, recipient_role=RecipientRole.OPERATOR))
    projection = project_communication(decision, CommunicationRepresentation.COMPACT_REFERENCED)
    assert "evidence:E1" not in projection.payload
    assert "evidence_ref:E1" in projection.payload
    assert_projection_preservation(decision, projection)
    assert_observable_evidence_recovery(decision, projection)


def test_boundary_experiment_rejects_silent_evidence_omission():
    state = unresolved_failure_state()
    decision = select_communicative_act(state, InteractionContext("operator", CommunicativeObjective.INFORM, recipient_role=RecipientRole.OPERATOR))
    projection = project_communication(decision, CommunicationRepresentation.CONCISE)
    assert "evidence:E1" not in projection.payload
    try:
        assert_observable_evidence_recovery(decision, projection)
    except EpistemicPreservationError:
        return
    raise AssertionError("silent evidence omission was not rejected")
