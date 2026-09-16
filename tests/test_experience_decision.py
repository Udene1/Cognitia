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


def test_confirmed_experience_can_change_candidate_selection():
    problem = "database outage queue stall"
    actions = ResearchSearchPlanner().plan(problem, max_actions=2).actions
    baseline = ExperienceAwareActionSelector().select(problem, actions, ExperienceLedger())
    experienced = ExperienceAwareActionSelector().select(
        problem,
        actions,
        ExperienceLedger((make_experience("x", EpistemicOutcome.CONFIRMED, problem),)),
    )
    assert experienced.selected.action.query.objective != baseline.selected.action.query.objective


def test_refuted_experience_can_defeat_prior_positive_influence():
    problem = "database outage queue stall"
    actions = ResearchSearchPlanner().plan(problem, max_actions=2).actions
    ledger = ExperienceLedger(
        (
            make_experience("positive", EpistemicOutcome.CONFIRMED, problem),
            make_experience("negative-1", EpistemicOutcome.REFUTED, problem),
            make_experience("negative-2", EpistemicOutcome.REFUTED, problem),
        )
    )
    decision = ExperienceAwareActionSelector().select(problem, actions, ledger)
    assert decision.selected.action.query.objective == actions[1].query.objective
