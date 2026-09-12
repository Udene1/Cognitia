from cognitia.failure_analysis import FailureAnalyzer, FailureClass, FailureObservation


def test_failure_diagnosis_targets_smallest_missing_machinery():
    failure = FailureObservation(
        attempt_id="a1",
        task="predict outcome",
        description="The procedure has no representation for hidden state.",
        failure_class=FailureClass.MISSING_REPRESENTATION,
    )

    diagnosis = FailureAnalyzer().diagnose(failure)

    assert diagnosis.capability == "representation_construction"
    assert diagnosis.failure_class is FailureClass.MISSING_REPRESENTATION
    assert diagnosis.confidence > 0


def test_explicit_missing_capability_wins_over_generic_failure_mapping():
    failure = FailureObservation(
        attempt_id="a2",
        task="solve",
        description="required operation unavailable",
        failure_class=FailureClass.MISSING_ALGORITHM,
        required_capability="causal_inference",
    )

    diagnosis = FailureAnalyzer().diagnose(failure, available_capabilities=("search",))

    assert diagnosis.capability == "causal_inference"
    assert diagnosis.confidence >= 0.9
