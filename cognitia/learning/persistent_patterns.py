"""Persist context-conditioned patterns learned from Cognitia experience memory."""

from __future__ import annotations

from typing import Iterable, Sequence
from uuid import NAMESPACE_URL, uuid5

from cognitia.memory import Experience
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge.persistent import PersistentKnowledgeStore

from .conditional import ConditionalPatternLearner


class PersistentPatternLearner:
    """Turn repeated experience outcomes into durable, provenance-backed knowledge.

    The learner stores patterns, not causal laws. Context fields are explicitly
    selected by the caller so volatile identifiers such as individual event IDs
    do not accidentally prevent generalization.
    """

    def __init__(self, store: PersistentKnowledgeStore) -> None:
        self._store = store
        self._learner = ConditionalPatternLearner()

    def learn_and_persist(
        self,
        experiences: Iterable[Experience],
        *,
        context_keys: Sequence[str],
        scope: str = "learned_patterns",
    ) -> tuple[KnowledgeItem, ...]:
        """Learn contextual patterns and persist only newly observed patterns."""
        experiences = tuple(experiences)
        selected = tuple(context_keys)
        if len(set(selected)) != len(selected):
            raise ValueError("context_keys must be unique")
        if not selected:
            raise ValueError("at least one context key is required")
        if not scope.strip():
            raise ValueError("scope must not be empty")

        projected = tuple(
            _project_experience(experience, selected) for experience in experiences
        )
        patterns = self._learner.learn(projected)
        items: list[KnowledgeItem] = []

        for pattern in patterns:
            context = dict(pattern.context)
            identity = f"{scope}:{pattern.action}:{sorted(context.items())}"
            item_id = str(uuid5(NAMESPACE_URL, identity))
            if any(existing.id == item_id for existing in self._store.all()):
                continue

            items.append(
                self._store.add(
                    KnowledgeItem(
                        subject=pattern.action,
                        predicate="performed_as_pattern",
                        value={
                            "context": context,
                            "positive": pattern.positive,
                            "negative": pattern.negative,
                            "neutral": pattern.neutral,
                            "observations": pattern.observations,
                            "success_rate": pattern.success_rate,
                        },
                        source=KnowledgeSource(
                            kind="experience_learning",
                            reference=f"memory:conditional:{scope}",
                            reliability=1.0,
                        ),
                        id=item_id,
                        scope=scope,
                    )
                )
            )
        return tuple(items)


def _project_experience(experience: Experience, keys: Sequence[str]) -> Experience:
    """Create a learning view containing only deliberately selected context."""
    return Experience(
        context={key: experience.context[key] for key in keys if key in experience.context},
        action=experience.action,
        observation=experience.observation,
        outcome=experience.outcome,
        id=experience.id,
        occurred_at=experience.occurred_at,
    )
