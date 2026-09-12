from cognitia.acquisition_engine import CapabilityAcquisitionEngine, CapabilityGapSignal
from cognitia.capability_acquisition import Operation, ReasoningTrace
from cognitia.failure_analysis import FailureAnalyzer, FailureClass, FailureObservation


def test_failure_diagnosis_becomes_an_acquisition_signal():
    failure = FailureObservation(
        attempt_id="attempt-1",
        task="classify motion",
        description="No reusable procedure exists for the required transformation.",
        failure_class=FailureClass.MISSING_ALGORITHM,
    )
    diagnosis = FailureAnalyzer().diagnose(failure)
    signal = CapabilityGapSignal.from_diagnosis(
        diagnosis,
        representation="structured transformation procedure",
    )

    assert signal.required_capability == "algorithm_construction"
    assert signal.candidate_name == "algorithm_construction"
    assert signal.allow_construction is False


def test_acquisition_still_prefers_learning_over_construction():
    add = Operation("add", lambda value: value + 1)
    traces = (
        ReasoningTrace("t1", ("add",), 1, 2, "counter"),
        ReasoningTrace("t2", ("add",), 2, 3, "counter"),
    )
    signal = CapabilityGapSignal(
        required_capability="increment",
        candidate_name="increment",
        representation="counter increment",
        traces=traces,
        allow_construction=True,
    )

    plan = CapabilityAcquisitionEngine({"add": add}).plan(signal)

    assert plan.decision.mode.value == "learn_procedure"
