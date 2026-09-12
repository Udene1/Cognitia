"""Durable cognitive state primitives.

The cognitive layer should not care whether memory is JSON, SQLite, or another
backend. This module provides a small durable event journal for state that is
not yet represented by a dedicated relational model (hypotheses, candidate
metadata, promotion history, and other cognitive records).

Events are append-only. Replaying them is deliberately explicit: persistence
is storage, not truth. A stored event remains evidence with provenance and does
not become a belief merely because it survived a restart.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable
from uuid import uuid4


@dataclass(frozen=True)
class DurableEvent:
    """An append-only cognitive event with explicit source and payload."""

    kind: str
    payload: dict[str, Any]
    source: str
    id: str = ""
    occurred_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("event kind is required")
        if not self.source.strip():
            raise ValueError("event source is required")
        if not isinstance(self.payload, dict):
            raise TypeError("event payload must be a dictionary")
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now(timezone.utc))


class SQLiteCognitiveJournal:
    """Durable append-only journal for cognitive state without callable code."""

    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteCognitiveJournal":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def append(self, event: DurableEvent) -> DurableEvent:
        try:
            payload = json.dumps(event.payload, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise TypeError("event payload must be JSON-serializable") from exc
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO cognitive_events (id, kind, source, payload_json, occurred_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (event.id, event.kind, event.source, payload, event.occurred_at.isoformat()),
            )
        return event

    def append_many(self, events: Iterable[DurableEvent]) -> tuple[DurableEvent, ...]:
        values = tuple(events)
        for event in values:
            try:
                json.dumps(event.payload, ensure_ascii=False, sort_keys=True)
            except (TypeError, ValueError) as exc:
                raise TypeError("event payload must be JSON-serializable") from exc
        with self._connection:
            self._connection.executemany(
                """
                INSERT INTO cognitive_events (id, kind, source, payload_json, occurred_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                [
                    (e.id, e.kind, e.source, json.dumps(e.payload, ensure_ascii=False, sort_keys=True), e.occurred_at.isoformat())
                    for e in values
                ],
            )
        return values

    def all(self) -> tuple[DurableEvent, ...]:
        rows = self._connection.execute(
            "SELECT * FROM cognitive_events ORDER BY occurred_at, id"
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def by_kind(self, kind: str) -> tuple[DurableEvent, ...]:
        rows = self._connection.execute(
            "SELECT * FROM cognitive_events WHERE kind = ? ORDER BY occurred_at, id",
            (kind,),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def _initialize(self) -> None:
        with self._connection:
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cognitive_events (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    occurred_at TEXT NOT NULL
                )
                """
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_cognitive_events_kind ON cognitive_events(kind)"
            )
            self._connection.execute(
                "INSERT INTO metadata(key, value) VALUES ('cognitive_schema_version', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(self.SCHEMA_VERSION),),
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> DurableEvent:
        return DurableEvent(
            id=row["id"],
            kind=row["kind"],
            source=row["source"],
            payload=json.loads(row["payload_json"]),
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
        )
