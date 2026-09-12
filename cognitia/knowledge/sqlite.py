"""SQLite-backed durable knowledge storage for Cognitia."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sqlite3

from .model import KnowledgeItem, KnowledgeSource


class SQLiteKnowledgeStore:
    """Durable local knowledge store with explicit provenance.

    SQLite is the first real persistence boundary for Cognitia's long-lived
    knowledge. Values are stored as JSON so the cognitive model remains
    independent of SQLite while the storage layer stays inspectable and
    transactional.
    """

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

    def __enter__(self) -> "SQLiteKnowledgeStore":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def add(self, item: KnowledgeItem) -> KnowledgeItem:
        try:
            value = json.dumps(item.value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise TypeError("knowledge value must be JSON-serializable") from exc

        with self._connection:
            self._connection.execute(
                """
                INSERT INTO knowledge (
                    id, subject, predicate, value_json, source_kind,
                    source_reference, source_reliability, learned_at, scope
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    subject = excluded.subject,
                    predicate = excluded.predicate,
                    value_json = excluded.value_json,
                    source_kind = excluded.source_kind,
                    source_reference = excluded.source_reference,
                    source_reliability = excluded.source_reliability,
                    learned_at = excluded.learned_at,
                    scope = excluded.scope
                """,
                (
                    item.id,
                    item.subject,
                    item.predicate,
                    value,
                    item.source.kind,
                    item.source.reference,
                    item.source.reliability,
                    item.learned_at.isoformat(),
                    item.scope,
                ),
            )
        return item

    def all(self) -> tuple[KnowledgeItem, ...]:
        rows = self._connection.execute(
            "SELECT * FROM knowledge ORDER BY learned_at, id"
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def query(
        self,
        *,
        subject: str | None = None,
        predicate: str | None = None,
        scope: str | None = None,
    ) -> tuple[KnowledgeItem, ...]:
        clauses: list[str] = []
        parameters: list[str] = []
        if subject is not None:
            clauses.append("subject = ?")
            parameters.append(subject)
        if predicate is not None:
            clauses.append("predicate = ?")
            parameters.append(predicate)
        if scope is not None:
            clauses.append("scope = ?")
            parameters.append(scope)

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"SELECT * FROM knowledge{where} ORDER BY learned_at, id",
            parameters,
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def _initialize(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    source_reference TEXT NOT NULL,
                    source_reliability REAL NOT NULL,
                    learned_at TEXT NOT NULL,
                    scope TEXT NOT NULL
                )
                """
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_knowledge_subject ON knowledge(subject)"
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_knowledge_predicate ON knowledge(predicate)"
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_knowledge_scope ON knowledge(scope)"
            )
            self._connection.execute(
                """
                INSERT INTO metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(self.SCHEMA_VERSION),),
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> KnowledgeItem:
        return KnowledgeItem(
            id=row["id"],
            subject=row["subject"],
            predicate=row["predicate"],
            value=json.loads(row["value_json"]),
            source=KnowledgeSource(
                kind=row["source_kind"],
                reference=row["source_reference"],
                reliability=row["source_reliability"],
            ),
            learned_at=datetime.fromisoformat(row["learned_at"]),
            scope=row["scope"],
        )
