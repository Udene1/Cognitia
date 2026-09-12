"""Durable local knowledge storage for Cognitia."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .model import KnowledgeItem, KnowledgeSource


class KnowledgePersistenceError(RuntimeError):
    """Raised when durable knowledge cannot be loaded or written safely."""


class PersistentKnowledgeStore:
    """JSON-backed knowledge store with atomic replacement on writes.

    The file is deliberately boring and inspectable. It gives Cognitia durable
    knowledge during early experiments without committing the architecture to a
    database before the semantics of knowledge are stable.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self._items: dict[str, KnowledgeItem] = {}
        self._load()

    def add(self, item: KnowledgeItem) -> KnowledgeItem:
        self._items[item.id] = item
        self._flush()
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
        return tuple(
            item
            for item in self._items.values()
            if (subject is None or item.subject == subject)
            and (predicate is None or item.predicate == predicate)
            and (scope is None or item.scope == scope)
        )

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ValueError("knowledge file must contain a list")
            for raw in payload:
                source = KnowledgeSource(**raw["source"])
                item = KnowledgeItem(
                    subject=raw["subject"],
                    predicate=raw["predicate"],
                    value=raw["value"],
                    source=source,
                    id=raw["id"],
                    learned_at=datetime.fromisoformat(raw["learned_at"]),
                    scope=raw["scope"],
                )
                self._items[item.id] = item
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise KnowledgePersistenceError(
                f"could not load knowledge from {self.path}"
            ) from exc

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = []
        for item in self._items.values():
            raw = asdict(item)
            raw["source"] = asdict(item.source)
            raw["learned_at"] = item.learned_at.isoformat()
            payload.append(raw)
        try:
            with NamedTemporaryFile(
                "w", encoding="utf-8", dir=self.path.parent, delete=False
            ) as temporary:
                json.dump(payload, temporary, ensure_ascii=False, indent=2, sort_keys=True)
                temporary.write("\n")
                temporary_path = Path(temporary.name)
            os.replace(temporary_path, self.path)
        except OSError as exc:
            if "temporary_path" in locals():
                temporary_path.unlink(missing_ok=True)
            raise KnowledgePersistenceError(
                f"could not persist knowledge to {self.path}"
            ) from exc
