import pytest

from cognitia.capability_acquisition import (
    AcquisitionMode,
    Operation,
    ReasoningTrace,
    compose_capability,
    construct_capability,
    learn_procedure,
)


def test_composes_existing_operations_into_new_capability() -> None:
    candidate = compose_capability(
        "double_then_increment",
        (Operation("double", lambda x: x * 2), Operation("increment", lambda x: x + 1)),
        representation="x -> 2x -> 2x+1",
    )

    assert candidate.mode is AcquisitionMode.COMPOSE
    assert candidate.execute(4) == 9


def test_learns_repeated_reasoning_sequence() -> None:
    operations = {
        "double": Operation("double", lambda x: x * 2),
        "increment": Operation("increment", lambda x: x + 1),
    }
    traces = (
        ReasoningTrace("t1", ("double", "increment"), 1, 3),
        ReasoningTrace("t2", ("double", "increment"), 4, 9),
    )

    candidate = learn_procedure(
        "learned_transform",
        traces,
        operations,
        representation="repeated successful double-then-increment procedure",
    )

    assert candidate.mode is AcquisitionMode.LEARN_PROCEDURE
    assert candidate.source_trace_ids == ("t1", "t2")
    assert candidate.execute(7) == 15


def test_procedure_requires_consistent_traces() -> None:
    operations = {"double": Operation("double", lambda x: x * 2)}
    traces = (
        ReasoningTrace("t1", ("double",), 1, 2),
        ReasoningTrace("t2", ("double", "double"), 1, 4),
    )

    with pytest.raises(ValueError, match="same operation sequence"):
        learn_procedure("bad", traces, operations, representation="x -> 2x")


def test_constructed_code_is_a_candidate_not_live_deployment() -> None:
    candidate = construct_capability(
        "square",
        lambda x: x * x,
        operations=("multiply",),
        representation="x -> x²",
        code_artifact="def square(x): return x * x",
    )

    assert candidate.mode is AcquisitionMode.CONSTRUCT
    assert candidate.code_artifact is not None
    assert candidate.execute(5) == 25
