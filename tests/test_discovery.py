import pytest

from cognitia.discovery import (
    DiscoveryWorkspace,
    ExplanationAssessment,
    ExplanationStatus,
    ExplanatoryGap,
    HypothesisCandidate,
    Observation,
    unresolved_observations,
)


def test_unexplained_observation_becomes_explanatory_gap():
    workspace = DiscoveryWorkspace()
    workspace.add_observation(Observation("o1", "effect appears only under condition A"))
    workspace.add_observation(Observation("o2", "baseline remains stable"))
    workspace.assess(ExplanationAssessment("o1", ExplanationStatus.UNEXPLAINED, "existing model predicts no effect"))
    workspace.assess(ExplanationAssessment("o2", ExplanationStatus.EXPLAINED))

    gaps = workspace.identify_gaps()

    assert len(gaps) == 1
    assert gaps[0].observation_ids == ("o1",)
    assert gaps[0].missing_aspects == ("existing model predicts no effect",)


def test_candidate_records_origin_but_is_not_declared_true():
    workspace = DiscoveryWorkspace()
    workspace.add_observation(Observation("o1", "unexpected effect"))
    workspace.assess(ExplanationAssessment("o1", ExplanationStatus.UNEXPLAINED))
    workspace.identify_gaps()

    candidate = HypothesisCandidate(
        id="h1",
        proposition="condition A changes the mechanism rather than the magnitude",
        derived_from_gap=("o1",),
        predictions=("effect persists when magnitude is controlled",),
        novelty_status="unassessed",
    )
    workspace.register_hypothesis(candidate)

    assert workspace.hypotheses["h1"].epistemic_status == "hypothesis"
    assert workspace.hypotheses["h1"].novelty_status == "unassessed"


def test_hypothesis_cannot_reference_unknown_observations():
    workspace = DiscoveryWorkspace()
    with pytest.raises(ValueError):
        workspace.register_hypothesis(
            HypothesisCandidate("h1", "something", ("missing",))
        )


def test_unresolved_observations_is_deterministic():
    assessments = [
        ExplanationAssessment("o1", ExplanationStatus.EXPLAINED),
        ExplanationAssessment("o2", ExplanationStatus.CONTRADICTED),
        ExplanationAssessment("o3", ExplanationStatus.UNEXPLAINED),
    ]
    assert unresolved_observations(assessments) == ("o2", "o3")


def test_gap_requires_an_observation_and_missing_aspect():
    with pytest.raises(ValueError):
        ExplanatoryGap((), ("missing",))
    with pytest.raises(ValueError):
        ExplanatoryGap(("o1",), ())
