from cognitia.acquisition_engine import CapabilityAcquisitionEngine, CapabilityGapSignal
from cognitia.capability_acquisition import AcquisitionMode, Operation, ReasoningTrace


def test_engine_learns_repeated_successful_procedure():
    operations = {
        "double": Operation("double", lambda value: value * 2),
        "increment": Operation("increment", lambda value: value + 1),
    }
    traces = (
        ReasoningTrace("t1", ("double", "increment"), 2, 5),
        ReasoningTrace("t2", ("double", "increment"), 4, 9),
    )
    signal = CapabilityGapSignal(
        required_capability="scaled_increment",
        candidate_name="scaled_increment",
        representation="x -> 2x + 1",
        traces=traces,
    )

    plan = CapabilityAcquisitionEngine(operations).plan(signal)

    assert plan.decision.mode is AcquisitionMode.LEARN_PROCEDURE
    assert plan.candidate.execute(7) == 15
    assert plan.decision.source_trace_ids == ("t1", "t2")


def test_engine_composes_when_sequence_is_known_but_not_repeated():
    operations = {
        "double": Operation("double", lambda value: value * 2),
        "increment": Operation("increment", lambda value: value + 1),
    }
    signal = CapabilityGapSignal(
        required_capability="scaled_increment",
        candidate_name="scaled_increment",
        representation="x -> 2x + 1",
        operation_sequence=("double", "increment"),
    )

    plan = CapabilityAcquisitionEngine(operations).plan(signal)

    assert plan.decision.mode is AcquisitionMode.COMPOSE
    assert plan.candidate.execute(3) == 7


def test_engine_constructs_only_when_explicitly_authorized():
    signal = CapabilityGapSignal(
        required_capability="square_root",
        candidate_name="square_root",
        representation="nonlinear root operation",
        allow_construction=True,
    )
    engine = CapabilityAcquisitionEngine({})

    plan = engine.plan(signal, constructor=lambda _: (lambda value: value ** 0.5, "candidate-code:sqrt"))

    assert plan.decision.mode is AcquisitionMode.CONSTRUCT
    assert plan.candidate.execute(81) == 9
    assert plan.candidate.code_artifact == "candidate-code:sqrt"


def test_engine_does_not_silently_construct_missing_capability():
    signal = CapabilityGapSignal(
        required_capability="square_root",
        candidate_name="square_root",
        representation="nonlinear root operation",
    )
    engine = CapabilityAcquisitionEngine({})

    try:
        engine.plan(signal)
    except ValueError as exc:
        assert "no viable acquisition path" in str(exc)
    else:
        raise AssertionError("missing capability must not be silently constructed")
