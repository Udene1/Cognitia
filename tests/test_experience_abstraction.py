from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ObservedConsequence
from cognitia.experience_abstraction import ExperienceAbstractionEngine


def make(item_id, problem, outcome):
    state = CognitiveState(problem, hypothesis_ids=("researcher-only",), uncertainty=("researcher-only",))
    return Experience(item_id, state, "search", "test", ExpectedConsequence("reduce uncertainty"), ObservedConsequence("reduce uncertainty", outcome), state)


def test_abstraction_does_not_depend_on_researcher_state_ids():
    engine = ExperienceAbstractionEngine()
    first = make("a", "Why did the payment queue stall after an outage?", EpistemicOutcome.CONFIRMED)
    second = make("b", "Why did the archive queue stop after a network failure?", EpistemicOutcome.CONFIRMED)
    assert engine.abstract(first).features == engine.abstract(second).features


def test_contradiction_changes_abstraction_support():
    engine = ExperienceAbstractionEngine()
    first = make("a", "Why did the payment queue stall after an outage?", EpistemicOutcome.CONFIRMED)
    hypotheses = engine.induce((first,))
    revised = engine.revise(hypotheses, make("b", "Why did the reporting queue stop after a migration?", EpistemicOutcome.REFUTED))
    assert revised[0].consistency != hypotheses[0].consistency
