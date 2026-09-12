"""Persist learned solution patterns for transfer into later problem solving.

A stored solution keeps both the concrete implementation and the abstract
computational logic.  Persistence is deliberately separate from reasoning:
storing a pattern does not make it universally correct.
"""
from __future__ import annotations

from typing import Iterable
from uuid import NAMESPACE_URL, uuid5

from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge.persistent import PersistentKnowledgeStore
from cognitia.memory import Experience

from .solution_patterns import SolutionPatternLearner


class PersistentSolutionPatternLearner:
    """Learn solution patterns from experiences and persist them as knowledge."""

    def __init__(self, store: PersistentKnowledgeStore) -> None:
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
        for pattern in patterns:
            identity = (
                f"{scope}:{pattern.problem}:{pattern.logic}:"
                f"{pattern.implementation}:{pattern.language}:{pattern.context}"
            )
            item_id = str(uuid5(NAMESPACE_URL, identity))
            if any(existing.id == item_id for existing in self._store.all()):
                continue
            items.append(
                self._store.add(
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
            )
        return tuple(items)

    def candidates(self, *, scope: str = "learned_solutions") -> tuple[KnowledgeItem, ...]:
        """Return persisted solution patterns for a fresh reasoning process."""
        return self._store.query(predicate="has_solution_pattern", scope=scope)
