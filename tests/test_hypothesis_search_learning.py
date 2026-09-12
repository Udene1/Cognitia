from cognitia.discovery_hypotheses import HypothesisTransform
from cognitia.learning.hypothesis_search import HypothesisSearchLearner
from cognitia.memory.experience import Experience, Outcome


def experience(transform: HypothesisTransform, kind: str) -> Experience:
    return Experience(
        context={"hypothesis_transform": transform.value},
        action="test_hypothesis",
        observation={"result": kind},
        outcome=Outcome(kind, f"{transform.value} produced {kind} result"),
    )


def test_search_strategy_is_learned_from_explicit_outcomes() -> None:
    experiences = [
        experience(HypothesisTransform.ADD_MISSING_VARIABLE, "positive"),
        experience(HypothesisTransform.ADD_MISSING_VARIABLE, "positive"),
        experience(HypothesisTransform.RELAX_ASSUMPTION, "negative"),
        experience(HypothesisTransform.RELAX_ASSUMPTION, "neutral"),
    ]
    ranked = HypothesisSearchLearner().rank(experiences)
    assert ranked[0].transform is HypothesisTransform.ADD_MISSING_VARIABLE
    assert ranked[0].success_rate == 1.0
    assert ranked[0].observations == 2
    assert ranked[1].success_rate == 0.0


def test_unrelated_experiences_do_not_become_search_strategy() -> None:
    unrelated = Experience(
        context={"domain": "engineering"},
        action="deploy",
        observation={"result": "success"},
        outcome=Outcome("positive", "deployment succeeded"),
    )
    assert HypothesisSearchLearner().learn((unrelated,)) == ()
