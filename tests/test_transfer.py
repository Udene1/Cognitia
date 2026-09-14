from cognitia.capability_acquisition import ReasoningTrace
from cognitia.learning.transfer import assess_transfer


def test_repeated_same_context_can_transfer():
    traces = [ReasoningTrace("a", ("x", "y"), 1, 2, "database"), ReasoningTrace("b", ("x", "y"), 2, 3, "database")]
    result = assess_transfer(traces, "database")
    assert result.transferable
    assert result.confidence > 0.5
    assert not result.context_independent


def test_mixed_contexts_can_generalize_when_structure_repeats():
    traces = [ReasoningTrace("a", ("x", "y"), 1, 2, "database"), ReasoningTrace("b", ("x", "y"), 2, 3, "physics")]
    result = assess_transfer(traces, "economics")
    assert result.transferable
    assert result.context_independent
    assert result.target_context == "economics"
