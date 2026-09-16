from cognitia.experience import CognitiveState
from cognitia.information_need import InformationNeedDetector
from cognitia.operation_selection import OperationOption, OperationSelector
from cognitia.state_action_generation import AvailableOperation


OPS = (
    OperationOption(AvailableOperation("search", "use external evidence"), cost=0.40),
    OperationOption(AvailableOperation("compute", "compute a result"), cost=0.10),
    OperationOption(AvailableOperation("reason", "reason over existing evidence"), cost=0.05),
)


def test_freshness_state_can_prefer_external_evidence():
    state = CognitiveState("What is the latest inflation rate?")
    need = InformationNeedDetector().detect(state)
    choice = OperationSelector().assess(state, need, OPS)
    assert choice.selected is not None
    assert choice.selected.operation.name == "search"
    assert all(item.net_value is not None for item in choice.assessments)


def test_computation_state_can_prefer_computation_without_search():
    state = CognitiveState("Calculate 17 * 23.")
    need = InformationNeedDetector().detect(state)
    choice = OperationSelector().assess(state, need, OPS)
    assert choice.selected is not None
    assert choice.selected.operation.name == "compute"


def test_existing_evidence_can_prefer_reasoning_without_search():
    state = CognitiveState(
        "What follows from these observations?",
        evidence_ids=("e1", "e2"),
    )
    need = InformationNeedDetector().detect(state)
    choice = OperationSelector().assess(state, need, OPS)
    assert choice.selected is not None
    assert choice.selected.operation.name == "reason"


def test_selector_records_all_options_not_only_the_winner():
    state = CognitiveState("Why did this fail?", uncertainty=("cause",))
    need = InformationNeedDetector().detect(state)
    choice = OperationSelector().assess(state, need, OPS)
    assert {item.operation.name for item in choice.assessments} == {"search", "compute", "reason"}
