"""Explicit knowledge-ingestion API for humans and upstream extractors."""

from __future__ import annotations

from .model import KnowledgeItem, KnowledgeSource
from .store import KnowledgeStore


def teach(
    store: KnowledgeStore,
    *,
    subject: str,
    predicate: str,
    value: object,
    source_kind: str,
    source_reference: str,
    reliability: float = 1.0,
    scope: str = "general",
) -> KnowledgeItem:
    """Teach Cognitia one structured proposition with provenance.

    This is intentionally not an LLM ingestion pipeline yet. The first milestone
    makes the knowledge contract explicit so later document extractors must produce
    the same structured object rather than bypassing provenance.
    """
    item = KnowledgeItem(
        subject=subject,
        predicate=predicate,
        value=value,
        source=KnowledgeSource(
            kind=source_kind,
            reference=source_reference,
            reliability=reliability,
        ),
        scope=scope,
    )
    return store.add(item)
