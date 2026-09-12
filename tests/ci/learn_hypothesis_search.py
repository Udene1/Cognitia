"""CI experiment: discovery strategy improves from investigation consequences."""
from cognitia.discovery_hypotheses import HypothesisTransform
from cognitia.learning.hypothesis_search import HypothesisSearchLearner
from cognitia.memory.experience import Experience, Outcome


def episode(transform: HypothesisTransform, kind: str, case: str) -> Experience:
    return Experience(
        context={
            "hypothesis_transform": transform.value,
            "investigation_case": case,
        },
        action="test_hypothesis",
        observation={"tested": True, "case": case},
        outcome=Outcome(kind, f"{transform.value}: {kind}"),
    )


experiences = (
    episode(HypothesisTransform.ADD_MISSING_VARIABLE, "positive", "anomaly-a"),
    episode(HypothesisTransform.ADD_MISSING_VARIABLE, "positive", "anomaly-b"),
    episode(HypothesisTransform.RELAX_ASSUMPTION, "negative", "anomaly-a"),
    episode(HypothesisTransform.RELAX_ASSUMPTION, "neutral", "anomaly-b"),
)

ranked = HypothesisSearchLearner().rank(experiences)
assert ranked[0].transform is HypothesisTransform.ADD_MISSING_VARIABLE
assert ranked[0].success_rate == 1.0

print("SEARCH_STRATEGY_LEARNED")
print(f"TOP_TRANSFORM: {ranked[0].transform.value}")
print(f"TOP_SUCCESS_RATE: {ranked[0].success_rate}")
print("SEARCH_STRATEGY_TRANSFER_SUCCESS")
