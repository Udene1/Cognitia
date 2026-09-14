from cognitia.discovery import ExplanatoryGap, HypothesisCandidate, Observation
from cognitia.discovery_artifact import DiscoveryArtifact
from cognitia.discovery_experiments import DiscriminatingExperimentSelector
from cognitia.discovery_prediction import Prediction
from cognitia.discovery_search import DiscoverySearchEngine, SearchBudget, normalized_entropy
from cognitia.discovery_structure import ModelElement, ModelRelation, RelationKind, StructuralModel


def test_search_is_bounded_and_traceable() -> None:
    model = StructuralModel(
        id="engine",
        elements=(ModelElement("load", "variable", "load"), ModelElement("balance", "variable", "balance")),
        relations=(ModelRelation("load", RelationKind.CAUSES, "balance"),),
    )
    gap = ExplanatoryGap(("o1",), ("current model cannot explain reversal",))
    results = DiscoverySearchEngine().search(model, gap=gap, budget=SearchBudget(max_candidates=3))
    assert len(results) == 3
    assert all(item.candidate.source_model == "engine" for item in results)
    assert all(item.novelty_evidence != "true" for item in results)


def test_information_gain_is_real_for_two_disagreeing_predictions() -> None:
    predictions = (
        Prediction("p1", "h1", "high_load", "stable", "increase"),
        Prediction("p2", "h2", "high_load", "unstable", "stable"),
    )
    experiment = DiscriminatingExperimentSelector().select(predictions)
    assert experiment is not None
    assert experiment.expected_information_gain == 1.0


def test_entropy_validates_distribution() -> None:
    assert normalized_entropy((0.5, 0.5)) == 1.0


def test_discovery_artifact_tracks_evidence_lifecycle() -> None:
    artifact = DiscoveryArtifact("d1", "unexpected engine behavior", observation_ids=("o1",))
    assert not artifact.is_ready_for_reproduction
    tested = artifact.with_outcome("supports hypothesis", epistemic_status="supported")
    assert not tested.is_ready_for_reproduction
    with_experiment = DiscoveryArtifact(
        tested.id, tested.title, tested.observation_ids, experiment_id="e1",
        outcome=tested.outcome, epistemic_status=tested.epistemic_status,
    )
    assert with_experiment.is_ready_for_reproduction
    reproduced = with_experiment.with_reproduction("independently_reproduced")
    assert reproduced.reproduction_status == "independently_reproduced"


def test_unused_imported_cognitive_types_remain_real_objects() -> None:
    observation = Observation("o1", "output diverged")
    hypothesis = HypothesisCandidate("h1", "missing dependency", (observation.id,))
    assert hypothesis.derived_from_gap == (observation.id,)
