"""First process in the durable-cognition restart proof."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.durable import DurableEvent, SQLiteCognitiveJournal
from cognitia.knowledge import SQLiteKnowledgeStore
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.memory import Experience, Outcome, SQLiteExperienceStore


root = Path(os.environ["COGNITIA_PERSISTENCE_ROOT"])
root.mkdir(parents=True, exist_ok=True)

knowledge = KnowledgeItem(
    id="restart-proof-knowledge",
    subject="cognitia",
    predicate="learned_pattern",
    value={"family": "group_by_reduce", "confidence": 0.92},
    source=KnowledgeSource(kind="ci", reference="persistence_writer", reliability=1.0),
    scope="restart_proof",
)
experience = Experience(
    id="restart-proof-experience",
    context={"environment": "engineering", "case": "restart"},
    action="persist_learning",
    observation={"knowledge_id": knowledge.id},
    outcome=Outcome("positive", "survived process boundary"),
)

with SQLiteKnowledgeStore(root / "knowledge.sqlite") as store:
    store.add(knowledge)
with SQLiteExperienceStore(root / "experience.sqlite") as store:
    store.record(experience)
with SQLiteCognitiveJournal(root / "cognition.sqlite") as journal:
    journal.append(
        DurableEvent(
            id="restart-proof-event",
            kind="learning_commit",
            source="ci:persistence_writer",
            payload={"knowledge_id": knowledge.id, "experience_id": experience.id},
        )
    )

print("PERSISTENCE_WRITE_SUCCESS")
