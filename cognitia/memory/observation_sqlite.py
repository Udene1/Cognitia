"""SQLite-backed durable observation memory.

Observations are retained evidence, not automatically promoted knowledge. This
store makes the observation ledger survive process shutdown and restart when
its SQLite file lives on a durable filesystem.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3

from ..observation import Observation


class SQLiteObservationStore:
    """Durably retain source observations with lossless provenance fields."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteObservationStore":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def ingest(self, observation: Observation) -> Observation:
        existing = self._connection.execute(
            "SELECT * FROM observations WHERE id = ?", (observation.id,)
        ).fetchone()
        if existing is not None:
            recovered = self._from_row(existing)
            if recovered != observation:
                raise ValueError(f"observation id collision: {observation.id}")
            return observation

        with self._connection:
            self._connection.execute(
                """
                INSERT INTO observations (
                    id, environment, kind, subject, payload, source_uri,
                    observed_at, parent_ids_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.id,
                    observation.environment,
                    observation.kind,
                    observation.subject,
                    observation.payload,
                    observation.source_uri,
                    observation.observed_at,
                    _encode_tuple(observation.parent_ids),
                    _encode_pairs(observation.metadata),
                ),
            )
        return observation

    def get(self, observation_id: str) -> Observation:
        row = self._connection.execute(
            "SELECT * FROM observations WHERE id = ?", (observation_id,)
        ).fetchone()
        if row is None:
            raise KeyError(observation_id)
        return self._from_row(row)

    def all(self) -> tuple[Observation, ...]:
        rows = self._connection.execute(
            "SELECT * FROM observations ORDER BY id"
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def by_environment(self, environment: str) -> tuple[Observation, ...]:
        rows = self._connection.execute(
            "SELECT * FROM observations WHERE environment = ? ORDER BY id",
            (environment,),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def _initialize(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS observations (
                    id TEXT PRIMARY KEY,
                    environment TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    source_uri TEXT,
                    observed_at TEXT,
                    parent_ids_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Observation:
        return Observation(
            id=row["id"],
            environment=row["environment"],
            kind=row["kind"],
            subject=row["subject"],
            payload=row["payload"],
            source_uri=row["source_uri"],
            observed_at=row["observed_at"],
            parent_ids=tuple(_decode_tuple(row["parent_ids_json"])),
            metadata=tuple(_decode_pairs(row["metadata_json"])),
        )


def _encode_tuple(values: tuple[str, ...]) -> str:
    import json
    return json.dumps(values, ensure_ascii=False)


def _decode_tuple(value: str) -> list[str]:
    import json
    return list(json.loads(value))


def _encode_pairs(values: tuple[tuple[str, str], ...]) -> str:
    import json
    return json.dumps(values, ensure_ascii=False)


def _decode_pairs(value: str) -> list[tuple[str, str]]:
    import json
    return [tuple(item) for item in json.loads(value)]
