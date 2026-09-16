from cognitia.experience import (
    CognitiveState,
    EpistemicOutcome,
    ExpectedConsequence,
    Experience,
    ExperienceLedger,
    ObservedConsequence,
)
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner


def make_experience(experience_id: str, outcome: EpistemicOutcome, problem: str = "database outage queue stall") -> Experience:
    return Experience(
        experience_id=experience_id,
        prior_state=CognitiveState(problem, hypothesis_ids=("h",)),
        action="investigate database outage",
        rationale="test",
        expected=ExpectedConsequence("database evidence resolves cause"),
        observed=ObservedConsequence("database evidence resolves cause", outcome),
        state_update=CognitiveState(problem),
    )


def test_refuted_epistemic_outcome_counts_as_discrepancy_even_when_text_matches():
    item = make_experience("x", EpistemicOutcome.REFUTED)
    assert item.discrepancy is True


def test_confirmed_experience_influences_candidate_score():
    problem = "database outage queue stall"
    actions = ResearchSearchPlanner().plan(problem, max_actions=2).actions
    baseline = ExperienceAwareActionSelector().select(problem, actions, ExperienceLedger())
    experienced = ExperienceAwareActionSelector().select(
        problem,
        actions,
        ExperienceLedger((make_experience("x", EpistemicOutcome.CONFIRMED, problem),)),
    )
    assert experienced.selected.score > baseline.selected.score
    assert experienced.selected.relevant_experience_ids == ("x",)
    assert "confirmed" in experienced.selected.rationale


def test_refuted_experience_reduces_positive_influence_without_forcing_a_different_action():
    problem = "database outage queue stall"
    actions = ResearchSearchPlanner().plan(problem, max_actions=2).actions
    positive = ExperienceAwareActionSelector().select(
        problem,
        actions,
        ExperienceLedger((make_experience("positive", EpistemicOutcome.CONFIRMED, problem),)),
    )
    contradicted = ExperienceAwareActionSelector().select(
        problem,
        actions,
        ExperienceLedger((
            make_experience("positive", EpistemicOutcome.CONFIRMED, problem),
            make_experience("negative-1", EpistemicOutcome.REFUTED, problem),
            make_experience("negative-2", EpistemicOutcome.REFUTED, problem),
        )),
    )
    positive_scores = {item.action.query.objective: item.score for item in positive.candidates}
    contradicted_scores = {item.action.query.objective: item.score for item in contradicted.candidates}
    assert any(contradicted_scores[key] < positive_scores[key] for key in positive_scores)
    assert "negative-1" in contradicted.selected.relevant_experience_ids
    assert "negative-2" in contradicted.selected.relevant_experience_ids
    assert "refuted" in contradicted.selected.rationale
