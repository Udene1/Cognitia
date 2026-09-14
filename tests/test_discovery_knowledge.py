import pytest

from cognitia.discovery_artifact import DiscoveryArtifact
from cognitia.discovery_knowledge import DiscoveryKnowledgePromoter
from cognitia.knowledge.model import KnowledgeSource
from cognitia.knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore
from cognitia.durable import SQLiteCognitiveJournal


def artifact(status="supported", reproduction="independently_reproduced"):
    return DiscoveryArtifact("d1", "test discovery", observation_ids=("o1",), epistemic_status=status, reproduction_status=reproduction)


def test_discovery_requires_reproduction_before_knowledge():
    decision = DiscoveryKnowledgePromoter().assess(artifact(reproduction="not_attempted"), ())
    assert not decision.eligible
    assert decision.reason == "independent_reproduction_required"


def test_reproduced_discovery_can_be_promoted(tmp_path):
    with SQLiteCognitiveJournal(tmp_path / "cognition.sqlite") as journal:
        store = ValidatedKnowledgeStore(journal)
        tests = (KnowledgeTest("v1", "validated:d1", True, 0.95),)
        DiscoveryKnowledgePromoter().promote(store, artifact(), "the proposition", KnowledgeSource("experiment", "d1"), tests)
        assert store.recover()[0]["id"] == "validated:d1"


def test_failed_validation_blocks_promotion(tmp_path):
    with SQLiteCognitiveJournal(tmp_path / "cognition.sqlite") as journal:
        store = ValidatedKnowledgeStore(journal)
        with pytest.raises(ValueError):
            DiscoveryKnowledgePromoter().promote(store, artifact(), "the proposition", KnowledgeSource("experiment", "d1"),
                                                  (KnowledgeTest("v1", "validated:d1", False),))
