"""Knowledge consolidation gated by explicit successful tests.

Cognitia may remember candidates and experiences freely, but durable *knowledge*
is promoted only when its required tests have survived and no unresolved
challenge remains. Persistence is a consequence of validation, not validation
itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..durable import DurableEvent, SQLiteCognitiveJournal
from .model import KnowledgeItem


@dataclass(frozen=True)
class KnowledgeTest:
    id: str
    knowledge_id: str
    passed: bool
    reliability: float = 1.0
    challenge: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.knowledge_id.strip():
            raise ValueError("test identity is required")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("test reliability must be between 0 and 1")


class ValidatedKnowledgeStore:
    """A durable gate for propositions that have survived explicit tests."""

    def __init__(self, journal: SQLiteCognitiveJournal, *, min_reliability: float = 0.8) -> None:
        if not 0.0 <= min_reliability <= 1.0:
            raise ValueError("min_reliability must be between 0 and 1")
        self.journal = journal
        self.min_reliability = min_reliability

    def record_test(self, test: KnowledgeTest) -> DurableEvent:
        return self.journal.append(DurableEvent(
            kind="knowledge_test",
            source="knowledge_validation",
            payload={"id": test.id, "knowledge_id": test.knowledge_id, "passed": test.passed,
                     "reliability": test.reliability, "challenge": test.challenge},
        ))

    def promote(self, item: KnowledgeItem, tests: tuple[KnowledgeTest, ...]) -> DurableEvent:
        if not tests:
            raise ValueError("knowledge requires at least one test before promotion")
        if any(test.knowledge_id != item.id for test in tests):
            raise ValueError("all tests must reference the knowledge item")
        if any(not test.passed or test.challenge or test.reliability < self.min_reliability for test in tests):
            raise ValueError("knowledge has not survived its validation requirements")
        # Persist the tests and the resulting durable knowledge atomically in one journal transaction.
        events = [DurableEvent(
            kind="knowledge_test", source="knowledge_validation",
            payload={"id": t.id, "knowledge_id": t.knowledge_id, "passed": t.passed,
                     "reliability": t.reliability, "challenge": t.challenge},
        ) for t in tests]
        events.append(DurableEvent(
            kind="validated_knowledge", source="knowledge_validation",
            payload={"id": item.id, "subject": item.subject, "predicate": item.predicate,
                     "value": item.value, "source_kind": item.source.kind,
                     "source_reference": item.source.reference, "source_reliability": item.source.reliability,
                     "scope": item.scope, "test_ids": [t.id for t in tests],
                     "validation": "survived_explicit_tests"},
        ))
        return self.journal.append_many(events)[-1]

    def all(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("validated_knowledge"))

    def recover(self) -> tuple[dict[str, Any], ...]:
        """Restart-safe read path; only promoted knowledge is returned."""
        return self.all()
