from cognitia.acquisition_engine import CapabilityAcquisitionEngine, CapabilityGapSignal
from cognitia.capability_acquisition import AcquisitionMode, Operation, ReasoningTrace
from cognitia.failure_analysis import FailureClass, FailureObservation


def test_failure_becomes_canonical_gap_signal():
    failure = FailureObservation(
        attempt_id="a1",
        task="solve task",
        description="required operation unavailable",
        failure_class=FailureClass.MISSING_ALGORITHM,
    )

    signal = CapabilityGapSignal.from_failure(failure)

    assert signal.required_capability == "algorithm_construction"
    assert signal.candidate_name == "algorithm_construction"
    assert signal.representation == "algorithm_construction"


def test_engine_can_plan_directly_from_failed_attempt_when_repeated_trace_exists():
    failure = FailureObservation(
        attempt_id="a2",
        task="solve task",
        description="missing reusable procedure",
        failure_class=FailureClass.MISSING_PRIMITIVE,
    )
    traces = (
        ReasoningTrace("t1", ("double", "increment"), 2, 5),
        ReasoningTrace("t2", ("double", "increment"), 3, 7),
    )
    engine = CapabilityAcquisitionEngine({
        "double": Operation("double", lambda x: x * 2),
        "increment": Operation("increment", lambda x: x + 1),
    })

    signal = engine.signal_from_failure(failure, traces=traces)
    plan = engine.plan(signal)

    assert plan.decision.mode is AcquisitionMode.LEARN_PROCEDURE
    assert plan.candidate.execute(4) == 9


def test_failure_bridge_does_not_authorize_construction():
    failure = FailureObservation(
        attempt_id="a3",
        task="invent capability",
        description="no known machinery",
        failure_class=FailureClass.MISSING_ALGORITHM,
    )
    engine = CapabilityAcquisitionEngine({})
    signal = engine.signal_from_failure(failure)

    assert signal.allow_construction is False
    try:
        engine.plan(signal)
    except ValueError as exc:
        assert "construction is not authorized" in str(exc)
    else:
        raise AssertionError("missing capability must not silently construct")
