"""SQLite-backed durable episodic memory for Cognitia."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sqlite3

from .experience import Experience, Outcome


class SQLiteExperienceStore:
    """Durable action/consequence memory with lossless structured fields."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteExperienceStore":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def record(self, experience: Experience) -> Experience:
        try:
            context = json.dumps(experience.context, ensure_ascii=False, sort_keys=True)
            observation = json.dumps(
                experience.observation, ensure_ascii=False, sort_keys=True
            )
        except (TypeError, ValueError) as exc:
            raise TypeError("experience context and observation must be JSON-serializable") from exc

        with self._connection:
            self._connection.execute(
                """
                INSERT INTO experiences (
                    id, context_json, action, observation_json,
                    outcome_kind, outcome_description, outcome_value, occurred_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    context_json = excluded.context_json,
                    action = excluded.action,
                    observation_json = excluded.observation_json,
                    outcome_kind = excluded.outcome_kind,
                    outcome_description = excluded.outcome_description,
                    outcome_value = excluded.outcome_value,
                    occurred_at = excluded.occurred_at
                """,
                (
                    experience.id,
                    context,
                    experience.action,
                    observation,
                    experience.outcome.kind,
                    experience.outcome.description,
                    experience.outcome.value,
                    experience.occurred_at.isoformat(),
                ),
            )
        return experience

    def all(self) -> tuple[Experience, ...]:
        rows = self._connection.execute(
            "SELECT * FROM experiences ORDER BY occurred_at, id"
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def _initialize(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS experiences (
                    id TEXT PRIMARY KEY,
                    context_json TEXT NOT NULL,
                    action TEXT NOT NULL,
                    observation_json TEXT NOT NULL,
                    outcome_kind TEXT NOT NULL,
                    outcome_description TEXT NOT NULL,
                    outcome_value REAL,
                    occurred_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Experience:
        return Experience(
            id=row["id"],
            context=json.loads(row["context_json"]),
            action=row["action"],
            observation=json.loads(row["observation_json"]),
            outcome=Outcome(
                kind=row["outcome_kind"],
                description=row["outcome_description"],
                value=row["outcome_value"],
            ),
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
        )
