"""Persist learned solution patterns for transfer into later problem solving."""
from __future__ import annotations

from typing import Iterable, Protocol
from uuid import NAMESPACE_URL, uuid5

from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.memory import Experience

from .solution_patterns import SolutionPatternLearner


class KnowledgePersistence(Protocol):
    """Minimal persistence contract shared by JSON and SQLite knowledge stores."""

    def add(self, item: KnowledgeItem) -> KnowledgeItem: ...
    def all(self) -> tuple[KnowledgeItem, ...]: ...
    def query(
        self,
        *,
        subject: str | None = None,
        predicate: str | None = None,
        scope: str | None = None,
    ) -> tuple[KnowledgeItem, ...]: ...


class PersistentSolutionPatternLearner:
    """Learn solution patterns and persist them in any compatible durable store."""

    def __init__(self, store: KnowledgePersistence) -> None:
        self._store = store
        self._learner = SolutionPatternLearner()

    def learn_and_persist(
        self,
        experiences: Iterable[Experience],
        *,
        scope: str = "learned_solutions",
    ) -> tuple[KnowledgeItem, ...]:
        patterns = self._learner.learn(experiences)
        items: list[KnowledgeItem] = []
        existing_ids = {item.id for item in self._store.all()}
        for pattern in patterns:
            identity = (
                f"{scope}:{pattern.problem}:{pattern.logic}:"
                f"{pattern.implementation}:{pattern.language}:{pattern.context}"
            )
            item_id = str(uuid5(NAMESPACE_URL, identity))
            if item_id in existing_ids:
                continue
            item = self._store.add(
                KnowledgeItem(
                    subject=pattern.problem,
                    predicate="has_solution_pattern",
                    value={
                        "logic": pattern.logic,
                        "implementation": pattern.implementation,
                        "language": pattern.language,
                        "context": dict(pattern.context),
                        "positive": pattern.positive,
                        "negative": pattern.negative,
                        "neutral": pattern.neutral,
                        "observations": pattern.observations,
                        "success_rate": pattern.success_rate,
                    },
                    source=KnowledgeSource(
                        kind="solution_learning",
                        reference=f"memory:solutions:{scope}",
                        reliability=1.0,
                    ),
                    id=item_id,
                    scope=scope,
                )
            )
            items.append(item)
            existing_ids.add(item_id)
        return tuple(items)

    def candidates(self, *, scope: str = "learned_solutions") -> tuple[KnowledgeItem, ...]:
        return self._store.query(predicate="has_solution_pattern", scope=scope)
