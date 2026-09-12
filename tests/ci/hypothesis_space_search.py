"""CI research experiment: construct alternatives, predictions, and a discriminating test."""
from cognitia import (
    DiscriminatingExperimentSelector,
    ExplanatoryModel,
    HypothesisCandidate,
    HypothesisSpaceBuilder,
    PredictionDeriver,
)
from cognitia.discovery import ExplanatoryGap


gap = ExplanatoryGap(
    observation_ids=("anomaly-1",),
    missing_aspects=("the baseline model predicts stability, but measurements vary with load",),
)
model = ExplanatoryModel(
    id="baseline-model",
    proposition="output remains stable under the tested operating conditions",
    assumptions=("operating conditions are uniform", "the measured process has no unmodeled dependency"),
    variables=("load", "temperature"),
)

alternatives = HypothesisSpaceBuilder().build(
    model,
    gap,
    missing_variables=("queue_depth",),
)
assert alternatives
assert all(item.novelty_status == "unassessed" for item in alternatives)

# Two competing candidates are made explicit rather than inferred from prose.
h1 = HypothesisCandidate("h-load", "output increases when load is high", ("anomaly-1",))
h2 = HypothesisCandidate("h-stable", "output remains stable when load is high", ("anomaly-1",))
deriver = PredictionDeriver()
p1 = deriver.derive(h1, condition="load=high", expected="increase", falsifier="stable or decreasing")
p2 = deriver.derive(h2, condition="load=high", expected="stable", falsifier="increase")
experiment = DiscriminatingExperimentSelector().select((p1, p2))
assert experiment is not None
assert experiment.condition == "load=high"

print("HYPOTHESIS_SPACE_CONSTRUCTED")
print(f"ALTERNATIVES: {len(alternatives)}")
print("NOVELTY_CLAIM: NONE")
print(f"DISCRIMINATING_EXPERIMENT: {experiment.condition}")
print("DISCOVERY_SEARCH_SUCCESS")
