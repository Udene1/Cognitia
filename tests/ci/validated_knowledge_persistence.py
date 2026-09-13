"""Restart proof: only knowledge that survived validation is recovered."""
import os
from pathlib import Path

from cognitia.durable import SQLiteCognitiveJournal
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore

root = Path(os.environ.get("COGNITIA_VALIDATED_KNOWLEDGE_ROOT", ".ci/validated-knowledge"))
root.mkdir(parents=True, exist_ok=True)
db = root / "cognition.sqlite"

with SQLiteCognitiveJournal(db) as journal:
    store = ValidatedKnowledgeStore(journal)
    item = KnowledgeItem("transaction", "grouping", "by-account", KnowledgeSource("experiment", "ci:transfer"), id="vk-group-by-account")
    store.promote(item, (KnowledgeTest("vk-test-1", item.id, True, 0.99), KnowledgeTest("vk-test-2", item.id, True, 0.95)))

with SQLiteCognitiveJournal(db) as journal:
    recovered = ValidatedKnowledgeStore(journal).recover()
    assert len(recovered) == 1
    assert recovered[0]["id"] == "vk-group-by-account"
    assert recovered[0]["test_ids"] == ["vk-test-1", "vk-test-2"]
    assert recovered[0]["validation"] == "survived_explicit_tests"

print("VALIDATED_KNOWLEDGE_RESTART_SUCCESS")
print("RECOVERED_KNOWLEDGE:", recovered[0]["value"])
print("VALIDATION_TESTS:", recovered[0]["test_ids"])
