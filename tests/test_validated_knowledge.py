from cognitia.durable import SQLiteCognitiveJournal
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore


def test_only_test_survivors_become_recoverable_knowledge(tmp_path):
    path = tmp_path / "cognition.sqlite"
    source = KnowledgeSource("experiment", "test:1", reliability=1.0)
    item = KnowledgeItem("system", "has_property", "stable", source, id="k1")

    with SQLiteCognitiveJournal(path) as journal:
        store = ValidatedKnowledgeStore(journal)
        try:
            store.promote(item, (KnowledgeTest("t-fail", item.id, False, 1.0),))
        except ValueError:
            pass
        else:
            raise AssertionError("failed knowledge must not be promoted")
        assert store.all() == ()
        store.promote(item, (KnowledgeTest("t-pass", item.id, True, 0.95),))

    with SQLiteCognitiveJournal(path) as journal:
        recovered = ValidatedKnowledgeStore(journal).recover()
        assert len(recovered) == 1
        assert recovered[0]["id"] == "k1"
        assert recovered[0]["test_ids"] == ["t-pass"]
        assert recovered[0]["validation"] == "survived_explicit_tests"


def test_challenge_blocks_promotion(tmp_path):
    with SQLiteCognitiveJournal(tmp_path / "cognition.sqlite") as journal:
        store = ValidatedKnowledgeStore(journal)
        item = KnowledgeItem("x", "is", True, KnowledgeSource("test", "case"), id="k2")
        try:
            store.promote(item, (KnowledgeTest("challenge", item.id, True, 1.0, challenge=True),))
        except ValueError:
            pass
        else:
            raise AssertionError("challenged knowledge must not be promoted")
        assert store.all() == ()
