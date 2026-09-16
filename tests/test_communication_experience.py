from dataclasses import replace

from cognitia.communication_experience import (
    CommunicationConsequence,
    CommunicationPolicy,
    policy_state_delta,
)
from cognitia.communicative_cognition import (
    CommunicativeAct,
    CommunicativeObjective,
    InteractionContext,
    RecipientRole,
    select_communicative_act,
)
from tests.test_communicative_cognition import unresolved_failure_state


def test_fresh_policy_does_not_change_baseline_decision():
    state = unresolved_failure_state()
    baseline = select_communicative_act(
        state,
        InteractionContext("operator", CommunicativeObjective.INFORM, recipient_role=RecipientRole.OPERATOR),
    )
    adapted = CommunicationPolicy().select(baseline)
    assert adapted.selected_act is baseline.selected_act
    assert adapted.claim_ids == baseline.claim_ids
    assert adapted.evidence_ids == baseline.evidence_ids


def test_recorded_consequence_changes_policy_and_future_decision():
    state = unresolved_failure_state()
    baseline = select_communicative_act(
        state,
        InteractionContext("operator", CommunicativeObjective.INFORM, recipient_role=RecipientRole.OPERATOR),
    )
    policy = CommunicationPolicy()
    before = policy.state

    policy.record(
        "experience-report-stalled",
        baseline,
        CommunicationConsequence(
            decision_state_id=baseline.state_id,
            selected_act=baseline.selected_act,
            outcome="stalled",
            signal=-1.0,
            observation="recipient could not act on the report",
        ),
    )

    alternate = replace(baseline, selected_act=CommunicativeAct.EXPLAIN_UNCERTAINTY)
    policy.record(
        "experience-explain-useful",
        alternate,
        CommunicationConsequence(
            decision_state_id=alternate.state_id,
            selected_act=alternate.selected_act,
            outcome="useful",
            signal=1.0,
            observation="recipient identified the unresolved distinction",
        ),
    )

    after = policy.state
    assert policy_state_delta(before, after) == (
        (CommunicativeAct.EXPLAIN_UNCERTAINTY.value, 1.0),
        (CommunicativeAct.REPORT_CURRENT_STATE.value, -1.0),
    )

    future = policy.select(baseline)
    assert future.selected_act is CommunicativeAct.EXPLAIN_UNCERTAINTY
    assert len(policy.experiences) == 2
    policy.assert_experience_driven_change(baseline, future)


def test_fresh_policy_is_control_for_experience_driven_change():
    state = unresolved_failure_state()
    baseline = select_communicative_act(
        state,
        InteractionContext("operator", CommunicativeObjective.INFORM, recipient_role=RecipientRole.OPERATOR),
    )
    fresh = CommunicationPolicy().select(baseline)
    assert fresh.selected_act is CommunicativeAct.REPORT_CURRENT_STATE


def test_adaptation_preserves_epistemic_contract():
    state = unresolved_failure_state()
    baseline = select_communicative_act(
        state,
        InteractionContext("operator", CommunicativeObjective.INFORM, recipient_role=RecipientRole.OPERATOR),
    )
    policy = CommunicationPolicy()
    policy.record(
        "negative-report",
        baseline,
        CommunicationConsequence(baseline.state_id, baseline.selected_act, "stalled", -1.0, "missing actionable context"),
    )
    policy.record(
        "positive-explain",
        replace(baseline, selected_act=CommunicativeAct.EXPLAIN_UNCERTAINTY),
        CommunicationConsequence(baseline.state_id, CommunicativeAct.EXPLAIN_UNCERTAINTY, "useful", 1.0, "uncertainty became actionable"),
    )
    adapted = policy.select(baseline)
    assert adapted.state_id == baseline.state_id
    assert adapted.claim_ids == baseline.claim_ids
    assert adapted.evidence_ids == baseline.evidence_ids
    assert adapted.uncertainty == baseline.uncertainty
    assert adapted.epistemic_status == baseline.epistemic_status
    assert adapted.verification_requirement == baseline.verification_requirement
