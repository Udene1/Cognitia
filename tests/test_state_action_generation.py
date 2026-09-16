from cognitia.experience import CognitiveState
from cognitia.state_action_generation import AvailableOperation, StateActionGenerator


OPS = (
    AvailableOperation("inspect", "inspect an available source"),
    AvailableOperation("compare", "compare independent observations"),
)


def test_generation_uses_state_signals_not_expected_actions():
    state = CognitiveState(
        "why did the queue stop?",
        hypothesis_ids=("dependency",),
        uncertainty=("cause",),
    )
    actions = StateActionGenerator().generate(state, OPS)
    assert actions
    assert all(action.source_signals for action in actions)
    assert all("why did the queue stop?" in action.objective for action in actions)


def test_changed_state_changes_generated_objectives():
    generator = StateActionGenerator()
    first = CognitiveState("why did the queue stop?", uncertainty=("cause",))
    second = CognitiveState(
        "why did the queue stop?",
        evidence_ids=("observation-1",),
        uncertainty=("cause", "conflict"),
        goal="distinguish explanations",
    )
    a = {item.objective for item in generator.generate(first, OPS)}
    b = {item.objective for item in generator.generate(second, OPS)}
    assert a != b


def test_empty_operations_produce_no_candidates():
    state = CognitiveState("a problem")
    assert StateActionGenerator().generate(state, ()) == ()
