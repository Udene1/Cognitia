"""Persist only factual Git observations; derive learning through experience."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from .git_environment import GitRepositoryObserver
from .knowledge.model import KnowledgeItem, KnowledgeSource
from .knowledge.persistent import PersistentKnowledgeStore


class GitKnowledgeIngestor:
    """Persist repository-history facts without promoting commit meaning.

    Git is an observation environment. This compatibility component stores only
    directly observable metadata (existence, authorship, timestamps and change
    counts). It deliberately does not infer correctness, intent, causality,
    usefulness, or lessons from a commit. Those belong to the observation ->
    experience -> extraction pipeline.
    """

    _PREDICATES = (
        "repository", "author", "authored_at", "subject", "parent_ids",
        "files_changed", "insertions", "deletions",
    )

    def __init__(self, store: PersistentKnowledgeStore) -> None:
        self._store = store

    def ingest(self, observer: GitRepositoryObserver, *, limit: int | None = None) -> tuple[KnowledgeItem, ...]:
        """Store observable facts only; no learning claim is made by ingestion."""
        items: list[KnowledgeItem] = []
        existing = {item.id for item in self._store.all()}
        for commit in observer.commits(limit):
            source_reference = f"git-observation:{observer.repository}#{commit.commit_id}"
            values = {
                "repository": str(observer.repository), "author": commit.author,
                "authored_at": commit.authored_at.isoformat(), "subject": commit.subject,
                "parent_ids": commit.parent_ids, "files_changed": commit.files_changed,
                "insertions": commit.insertions, "deletions": commit.deletions,
            }
            for predicate in self._PREDICATES:
                item_id = str(uuid5(NAMESPACE_URL, f"{source_reference}:{predicate}"))
                if item_id in existing:
                    continue
                item = KnowledgeItem(
                    subject=commit.commit_id, predicate=predicate, value=values[predicate], id=item_id,
                    source=KnowledgeSource(kind="git_observation_fact", reference=source_reference, reliability=1.0),
                    scope="repository_observation",
                )
                items.append(self._store.add(item))
                existing.add(item_id)
        return tuple(items)
