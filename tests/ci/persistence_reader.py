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

# The durable stores are append-only and intentionally survive across CI
# runs. The restart-proof identifiers are reused by the proof, so validate
# the most recent matching lifecycle records rather than assuming historical
# state contains only one occurrence.
restart_candidates = tuple(
    item for item in candidates if item.get("candidate_id") == "restart-proof-candidate"
)
restart_evaluations = tuple(
    item for item in evaluations if item.get("candidate_id") == "restart-proof-candidate"
)
restart_builds = tuple(
    item for item in builds if item.get("build_id") == "restart-proof-build"
)

assert items
assert items[-1].id == "restart-proof-knowledge"
assert items[-1].value["family"] == "group_by_reduce"
assert items[-1].source.reference == "persistence_writer"
assert episodes
assert episodes[-1].id == "restart-proof-experience"
assert episodes[-1].outcome.kind == "positive"
assert events
assert events[-1].payload["knowledge_id"] == items[-1].id
assert restart_candidates
assert restart_evaluations
assert restart_builds

candidate = restart_candidates[-1]
evaluation = restart_evaluations[-1]
build = restart_builds[-1]

assert candidate["state"] == "held"
assert candidate["candidate"]["code_artifact"] == "restart-proof-artifact"
assert candidate["candidate"]["executable_rehydration_required"] is True
assert evaluation["regression"] == 0.1
assert evaluation["reason"] == "hold before promotion"
assert build["build_id"] == "restart-proof-build"
assert build["capabilities"][0]["status"] == "held"

print("RECOVERED_KNOWLEDGE: group_by_reduce")
print("RECOVERED_EXPERIENCE: persist_learning -> positive")
print("RECOVERED_EVENT: learning_commit")
print("RECOVERED_CANDIDATE: restart-proof-candidate -> held")
print("RECOVERED_EVALUATION: regression=0.1")
print("RECOVERED_BUILD: restart-proof-build")
print("PROCESS_RESTART_PERSISTENCE_SUCCESS")
