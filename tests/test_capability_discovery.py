from cognitia.capabilities import CapabilityAvailability, CapabilityGap
from cognitia.capability_acquisition import AcquisitionMode, Operation, ReasoningTrace
from cognitia.capability_discovery import CapabilityDiscoveryEngine


def gap():
    return CapabilityGap("summarization", CapabilityAvailability.MISSING, substitution_allowed=False)


def test_repeated_traces_select_procedure_learning():
    ops = {"double": Operation("double", lambda x: x * 2), "inc": Operation("inc", lambda x: x + 1)}
    traces = tuple(ReasoningTrace(str(i), ("double", "inc"), i, i * 2 + 1, "math") for i in range(3))
    decision = CapabilityDiscoveryEngine().decide(gap(), available_operations=ops, successful_traces=traces)
    assert decision.mode is AcquisitionMode.LEARN_PROCEDURE
    candidate = CapabilityDiscoveryEngine().acquire_candidate(decision, available_operations=ops, successful_traces=traces, representation="double then increment")
    assert candidate.execute(4) == 9
    assert candidate.source_trace_ids == ("0", "1", "2")


def test_existing_operations_are_composed_before_construction():
    ops = {"double": Operation("double", lambda x: x * 2), "inc": Operation("inc", lambda x: x + 1)}
    decision = CapabilityDiscoveryEngine().decide(gap(), available_operations=ops, construction_available=True)
    assert decision.mode is AcquisitionMode.COMPOSE
    assert "existing verified operations" in decision.reason


def test_construction_is_only_selected_when_no_reusable_machinery_exists():
    decision = CapabilityDiscoveryEngine().decide(gap(), available_operations={}, construction_available=True)
    assert decision.mode is AcquisitionMode.CONSTRUCT
    assert decision.confidence.value == "low"


def test_no_path_is_explicit():
    try:
        CapabilityDiscoveryEngine().decide(gap(), available_operations={}, construction_available=False)
    except ValueError as exc:
        assert "no acquisition path" in str(exc)
    else:
        raise AssertionError("expected missing acquisition path")
