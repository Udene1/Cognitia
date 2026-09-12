"""Fresh process that proves durable cognition survived the writer's exit."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.durable import SQLiteCognitiveJournal
from cognitia.knowledge import SQLiteKnowledgeStore
from cognitia.memory import SQLiteExperienceStore

root = Path(os.environ["COGNITIA_PERSISTENCE_ROOT"])

with SQLiteKnowledgeStore(root / "knowledge.sqlite") as knowledge:
    items = knowledge.query(subject="cognitia", predicate="learned_pattern", scope="restart_proof")
with SQLiteExperienceStore(root / "experience.sqlite") as experiences:
    episodes = experiences.all()
with SQLiteCognitiveJournal(root / "cognition.sqlite") as journal:
    events = journal.by_kind("learning_commit")

assert len(items) == 1
assert items[0].id == "restart-proof-knowledge"
assert items[0].value["family"] == "group_by_reduce"
assert items[0].source.reference == "persistence_writer"
assert len(episodes) == 1
assert episodes[0].id == "restart-proof-experience"
assert episodes[0].outcome.kind == "positive"
assert len(events) == 1
assert events[0].payload["knowledge_id"] == items[0].id

print("RECOVERED_KNOWLEDGE: group_by_reduce")
print("RECOVERED_EXPERIENCE: persist_learning -> positive")
print("RECOVERED_EVENT: learning_commit")
print("PROCESS_RESTART_PERSISTENCE_SUCCESS")
