"""Fresh process that proves durable cognition survived the writer's exit."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.durable import SQLiteCognitiveJournal
from cognitia.durable_cognition import DurableCognitiveLedger
from cognitia.knowledge import SQLiteKnowledgeStore
from cognitia.memory import SQLiteExperienceStore

root = Path(os.environ["COGNITIA_PERSISTENCE_ROOT"])

with SQLiteKnowledgeStore(root / "knowledge.sqlite") as knowledge:
    items = knowledge.query(subject="cognitia", predicate="learned_pattern", scope="restart_proof")
with SQLiteExperienceStore(root / "experience.sqlite") as experiences:
    episodes = experiences.all()
with SQLiteCognitiveJournal(root / "cognition.sqlite") as journal:
    events = journal.by_kind("learning_commit")
    ledger = DurableCognitiveLedger(journal)
    candidates = ledger.candidate_snapshots()
    evaluations = ledger.evaluations()
    builds = ledger.builds()

assert len(items) == 1
assert items[0].id == "restart-proof-knowledge"
assert items[0].value["family"] == "group_by_reduce"
assert items[0].source.reference == "persistence_writer"
assert len(episodes) == 1
assert episodes[0].id == "restart-proof-experience"
assert episodes[0].outcome.kind == "positive"
assert len(events) == 1
assert events[0].payload["knowledge_id"] == items[0].id

assert len(candidates) == 1
assert candidates[0]["candidate_id"] == "restart-proof-candidate"
assert candidates[0]["state"] == "held"
assert candidates[0]["candidate"]["code_artifact"] == "restart-proof-artifact"
assert candidates[0]["candidate"]["executable_rehydration_required"] is True
assert len(evaluations) == 1
assert evaluations[0]["regression"] == 0.1
assert evaluations[0]["reason"] == "hold before promotion"
assert len(builds) == 1
assert builds[0]["build_id"] == "restart-proof-build"
assert builds[0]["capabilities"][0]["status"] == "held"

print("RECOVERED_KNOWLEDGE: group_by_reduce")
print("RECOVERED_EXPERIENCE: persist_learning -> positive")
print("RECOVERED_EVENT: learning_commit")
print("RECOVERED_CANDIDATE: restart-proof-candidate -> held")
print("RECOVERED_EVALUATION: regression=0.1")
print("RECOVERED_BUILD: restart-proof-build")
print("PROCESS_RESTART_PERSISTENCE_SUCCESS")
