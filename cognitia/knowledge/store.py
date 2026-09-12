"""In-memory knowledge store for the first Cognitia experiment."""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import KnowledgeItem


@dataclass
class KnowledgeStore:
    """Small deterministic store; persistence can be introduced after semantics stabilize."""

    _items: dict[str, KnowledgeItem] = field(default_factory=dict)

    def add(self, item: KnowledgeItem) -> KnowledgeItem:
        self._items[item.id] = item
        return item

    def all(self) -> tuple[KnowledgeItem, ...]:
        return tuple(self._items.values())

    def query(
        self,
        *,
        subject: str | None = None,
        predicate: str | None = None,
        scope: str | None = None,
    ) -> tuple[KnowledgeItem, ...]:
        """Retrieve knowledge by structure, not text similarity alone."""
        return tuple(
            item
            for item in self._items.values()
            if (subject is None or item.subject == subject)
            and (predicate is None or item.predicate == predicate)
            and (scope is None or item.scope == scope)
        )
