from datetime import datetime, timedelta, timezone

from cognitia.discovery_artifact import DiscoveryArtifact, DurableDiscoveryArtifacts
from cognitia.discovery_experiments import DiscriminatingExperimentSelector
from cognitia.discovery_investigation import DiscoveryInvestigator
from cognitia.discovery_prediction import Prediction
from cognitia.discovery_search import DiscoverySearchEngine, SearchBudget
from cognitia.discovery_structure import ModelElement, StructuralModel
from cognitia.durable import SQLiteCognitiveJournal
from cognitia.environment import EnvironmentObservation
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore
from cognitia.web_evidence import WebEvidenceEvaluator


def test_multi_step_search_is_bounded_and_traceable():
    model = StructuralModel(id="m", elements=(ModelElement("a", "variable", "a"), ModelElement("b", "variable", "b")))
    result = DiscoverySearchEngine().search(model, budget=SearchBudget(max_candidates=7, max_depth=2))
    assert result
    assert max(item.depth for item in result) == 2
    assert all(item.derivation for item in result)
    assert len({item.candidate.id for item in result}) == len(result)


def test_information_gain_uses_actual_prior_entropy():
    predictions = (
        Prediction("p1", "h1", "load=high", "increase", "no increase"),
        Prediction("p2", "h2", "load=high", "stable", "increase"),
    )
    experiment = DiscriminatingExperimentSelector().select(predictions, priors=(0.9, 0.1))
    assert experiment is not None
    assert 0 < experiment.expected_information_gain < 1


def test_web_evidence_deduplicates_and_respects_temporal_validity():
    now = datetime.now(timezone.utc)
    observations = (
        EnvironmentObservation("1", "web:a", "same", 0.9, (("expires_at", (now + timedelta(hours=1)).isoformat()),)),
        EnvironmentObservation("2", "web:a", "same", 0.9, ()),
        EnvironmentObservation("3", "web:b", "future", 0.9, (("effective_at", (now + timedelta(hours=1)).isoformat()),)),
    )
    assessed = WebEvidenceEvaluator().assess(observations, now=now)
    assert [a.reason for a in assessed] == ["accepted_as_evidence", "duplicate", "not_yet_effective"]


def test_discovery_investigator_keeps_provider_as_evidence_source():
    class Source:
        def observe(self, objective, *, limit=10):
            return (EnvironmentObservation("1", "provider:test", objective, 0.9, ()),)
    class Gap:
        missing_aspect = "unknown relation"
    result = DiscoveryInvestigator(Source()).investigate(Gap())
    assert result.accepted[0].source == "provider:test"


def test_validated_knowledge_only_persists_after_surviving_test_and_restart(tmp_path):
    path = tmp_path / "cognition.db"
    item = KnowledgeItem("x", "is", "true", KnowledgeSource("test", "case", 1.0), id="k1")
    with SQLiteCognitiveJournal(path) as journal:
        store = ValidatedKnowledgeStore(journal)
        test = KnowledgeTest("t1", "k1", passed=True, reliability=1.0)
        store.promote(item, (test,))
    with SQLiteCognitiveJournal(path) as journal:
        assert journal.by_kind("validated_knowledge")[0].payload["id"] == "k1"
        assert ValidatedKnowledgeStore(journal).recover()[0]["validation"] == "survived_explicit_tests"


def test_failed_knowledge_test_cannot_be_promoted(tmp_path):
    path = tmp_path / "cognition.db"
    item = KnowledgeItem("x", "is", "true", KnowledgeSource("test", "case", 1.0), id="k2")
    with SQLiteCognitiveJournal(path) as journal:
        store = ValidatedKnowledgeStore(journal)
        try:
            store.promote(item, (KnowledgeTest("t2", "k2", passed=False),))
        except ValueError:
            pass
        else:
            raise AssertionError("failed knowledge must not be promoted")
        assert store.all() == ()


def test_discovery_artifact_survives_restart(tmp_path):
    path = tmp_path / "cognition.db"
    artifact = DiscoveryArtifact(id="d1", title="test", observation_ids=("o1",), epistemic_status="hypothesis")
    with SQLiteCognitiveJournal(path) as journal:
        DurableDiscoveryArtifacts(journal).record(artifact)
    with SQLiteCognitiveJournal(path) as journal:
        recovered = DurableDiscoveryArtifacts(journal).all()
        assert recovered[0]["id"] == "d1"
