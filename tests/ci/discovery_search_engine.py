"""Exercise bounded discovery search without an LLM or hand-written answer."""
from cognitia.discovery import ExplanatoryGap
from cognitia.discovery_artifact import DiscoveryArtifact
from cognitia.discovery_experiments import DiscriminatingExperimentSelector
from cognitia.discovery_prediction import Prediction
from cognitia.discovery_search import DiscoverySearchEngine, SearchBudget
from cognitia.discovery_structure import ModelElement, ModelRelation, RelationKind, StructuralModel


model = StructuralModel(
    id="engine-balance",
    elements=(
        ModelElement("load", "variable", "load"),
        ModelElement("balance", "variable", "balance"),
        ModelElement("output", "variable", "output"),
    ),
    relations=(
        ModelRelation("load", RelationKind.CAUSES, "balance"),
        ModelRelation("balance", RelationKind.CAUSES, "output"),
    ),
)
gap = ExplanatoryGap(
    observation_ids=("o-regression",),
    missing_aspects=("current model cannot explain degraded output after adding capability",),
    competing_explanations=("interaction effect", "new dependency"),
)

results = DiscoverySearchEngine().search(model, gap=gap, budget=SearchBudget(max_candidates=8))
assert results
assert all(item.candidate.source_model == model.id for item in results)
assert all(item.novelty_evidence != "true" for item in results)

predictions = (
    Prediction("p-existing", "existing-model", "high_load", "stable", "output rises"),
    Prediction("p-alternative", "alternative-model", "high_load", "unstable", "output remains stable"),
)
experiment = DiscriminatingExperimentSelector().select(predictions)
assert experiment is not None
assert experiment.expected_information_gain == 1.0

artifact = DiscoveryArtifact(
    id="d-engine-balance",
    title="engine balance regression",
    observation_ids=gap.observation_ids,
    model_id=model.id,
    hypothesis_ids=(results[0].candidate.id,),
    prediction_ids=(predictions[0].id, predictions[1].id),
    experiment_id=experiment.id,
)
assert artifact.is_ready_for_reproduction

print("DISCOVERY_SEARCH_ENGINE_SUCCESS")
print("CANDIDATES:", len(results))
print("EXPECTED_INFORMATION_GAIN:", experiment.expected_information_gain)
print("NOVELTY_CLAIM: NONE")
print("RESEARCH_ARTIFACT_READY: True")
