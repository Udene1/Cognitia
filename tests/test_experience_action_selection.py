from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ExperienceLedger, ObservedConsequence
from cognitia.experience_action_selection import ExperienceGeneratedActionSelector
from cognitia.state_action_generation import AvailableOperation, StateActionGenerator


OPERATIONS = (
    AvailableOperation("search", "search"),
    AvailableOperation("inspect", "inspect"),
    AvailableOperation("compute", "compute"),
)


def make_experience(item_id: str, outcome: EpistemicOutcome) -> Experience:
    state = CognitiveState("database outage", hypothesis_ids=("cause",), uncertainty=("cause",))
    return Experience(
        experience_id=item_id,
        prior_state=state,
        action="search",
        rationale="test",
        expected=ExpectedConsequence("reduce uncertainty"),
        observed=ObservedConsequence("reduce uncertainty", outcome),
        state_update=state,
    )


def select(state, ledger):
    actions = StateActionGenerator().generate(state, OPERATIONS, max_actions=6)
    return ExperienceGeneratedActionSelector().select(state, actions, ledger).selected.action.operation.name


def test_confirmed_experience_can_influence_generated_action_selection():
    state = CognitiveState("new surface", hypothesis_ids=("cause",), uncertainty=("cause",))
    assert select(state, ExperienceLedger()) == "compute"
    assert select(state, ExperienceLedger((make_experience("confirmed", EpistemicOutcome.CONFIRMED),))) == "search"


def test_refutation_can_defeat_prior_experience():
    state = CognitiveState("new surface", hypothesis_ids=("cause",), uncertainty=("cause",))
    ledger = ExperienceLedger((
        make_experience("confirmed", EpistemicOutcome.CONFIRMED),
        make_experience("refuted", EpistemicOutcome.REFUTED),
    ))
    assert select(state, ledger) == "compute"


def test_unrelated_structural_state_does_not_inherit_experience():
    state = CognitiveState("new material", hypothesis_ids=("material",), uncertainty=("material",))
    assert select(state, ExperienceLedger((make_experience("refuted", EpistemicOutcome.REFUTED),))) == "compute"
