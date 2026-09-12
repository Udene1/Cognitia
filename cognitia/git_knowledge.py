"""Persist factual knowledge observed from a real Git repository."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from .git_environment import GitRepositoryObserver
from .knowledge.model import KnowledgeItem, KnowledgeSource
from .knowledge.persistent import PersistentKnowledgeStore


class GitKnowledgeIngestor:
    """Convert Git observations into durable, provenance-backed knowledge.

    This records facts about repository history only. A commit's existence is
    not treated as evidence that the implementation was correct or successful.
    Effectiveness remains an experience/outcome question.
    """

    _PREDICATES = (
        "repository",
        "author",
        "authored_at",
        "subject",
        "parent_ids",
        "files_changed",
        "insertions",
        "deletions",
    )

    def __init__(self, store: PersistentKnowledgeStore) -> None:
        self._store = store

    def ingest(
        self,
        observer: GitRepositoryObserver,
        *,
        limit: int | None = None,
    ) -> tuple[KnowledgeItem, ...]:
        items: list[KnowledgeItem] = []
        for commit in observer.commits(limit):
            source_reference = f"git:{observer.repository}#{commit.commit_id}"
            values = {
                "repository": str(observer.repository),
                "author": commit.author,
                "authored_at": commit.authored_at.isoformat(),
                "subject": commit.subject,
                "parent_ids": commit.parent_ids,
                "files_changed": commit.files_changed,
                "insertions": commit.insertions,
                "deletions": commit.deletions,
            }
            for predicate in self._PREDICATES:
                item_id = str(
                    uuid5(
                        NAMESPACE_URL,
                        f"{source_reference}:{predicate}",
                    )
                )
                if any(existing.id == item_id for existing in self._store.all()):
                    continue
                item = KnowledgeItem(
                    subject=commit.commit_id,
                    predicate=predicate,
                    value=values[predicate],
                    source=KnowledgeSource(
                        kind="git_commit",
                        reference=source_reference,
                        reliability=1.0,
                    ),
                    id=item_id,
                    scope="repository_history",
                )
                items.append(self._store.add(item))
        return tuple(items)
