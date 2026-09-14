"""Transport durable SQLite cognitive state across ephemeral CI runners.

The runner filesystem is intentionally treated as temporary. This module
creates a portable, integrity-checked snapshot of SQLite databases and can
restore that snapshot into a fresh runner. Storage is transport only: restoring
state does not promote observations or events into knowledge.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import tarfile
import tempfile
from typing import Iterable


FORMAT_VERSION = 1


@dataclass(frozen=True)
class StateFile:
    path: str
    size: int
    sha256: str


def snapshot_sqlite_state(root: str | Path, archive: str | Path) -> tuple[StateFile, ...]:
    """Create a consistent, integrity-checked archive of SQLite state under root."""
    source_root = Path(root).expanduser().resolve()
    archive_path = Path(archive).expanduser().resolve()
    if not source_root.exists():
        raise FileNotFoundError(source_root)
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    database_paths = tuple(
        sorted(
            path
            for path in source_root.rglob("*")
            if path.is_file() and path.suffix in {".sqlite", ".db"}
        )
    )
    if not database_paths:
        raise ValueError(f"no SQLite databases found under {source_root}")

    with tempfile.TemporaryDirectory(prefix="cognitia-state-") as temp_dir:
        staging = Path(temp_dir) / "state"
        staging.mkdir()
        records: list[StateFile] = []
        for source in database_paths:
            relative = source.relative_to(source_root).as_posix()
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            _backup_and_check(source, destination)
            records.append(
                StateFile(
                    path=relative,
                    size=destination.stat().st_size,
                    sha256=_sha256(destination),
                )
            )

        manifest = {
            "format_version": FORMAT_VERSION,
            "files": [record.__dict__ for record in records],
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with tarfile.open(archive_path, "w:gz") as bundle:
            bundle.add(staging / "manifest.json", arcname="manifest.json")
            for record in records:
                bundle.add(staging / record.path, arcname=record.path)

    return tuple(records)


def restore_sqlite_state(archive: str | Path, root: str | Path) -> tuple[StateFile, ...]:
    """Restore and verify a state snapshot into root atomically per database."""
    archive_path = Path(archive).expanduser().resolve()
    destination_root = Path(root).expanduser().resolve()
    if not archive_path.exists():
        raise FileNotFoundError(archive_path)
    destination_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cognitia-restore-") as temp_dir:
        staging = Path(temp_dir) / "state"
        staging.mkdir()
        with tarfile.open(archive_path, "r:gz") as bundle:
            members = bundle.getmembers()
            for member in members:
                target = (staging / member.name).resolve()
                if not _inside(staging.resolve(), target):
                    raise ValueError(f"unsafe state archive member: {member.name}")
                if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                    raise ValueError(f"unsupported state archive member: {member.name}")
            bundle.extractall(staging)

        manifest_path = staging / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("format_version") != FORMAT_VERSION:
            raise ValueError("unsupported cognitive state format version")

        records = tuple(StateFile(**item) for item in manifest.get("files", []))
        if not records:
            raise ValueError("state manifest contains no databases")

        for record in records:
            staged = staging / record.path
            if not _inside(staging.resolve(), staged.resolve()):
                raise ValueError(f"unsafe state path: {record.path}")
            if not staged.is_file():
                raise ValueError(f"missing state database: {record.path}")
            if staged.stat().st_size != record.size or _sha256(staged) != record.sha256:
                raise ValueError(f"state integrity mismatch: {record.path}")
            _integrity_check(staged)

        for record in records:
            source = staging / record.path
            target = destination_root / record.path
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary_target = target.with_suffix(target.suffix + ".restore")
            shutil.copy2(source, temporary_target)
            temporary_target.replace(target)

    return records


def _backup_and_check(source: Path, destination: Path) -> None:
    connection = sqlite3.connect(source)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise ValueError(f"SQLite integrity check failed: {source}")
        backup = sqlite3.connect(destination)
        try:
            connection.backup(backup)
            backup.commit()
        finally:
            backup.close()
    finally:
        connection.close()
    _integrity_check(destination)


def _integrity_check(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise ValueError(f"SQLite integrity check failed: {path}")
    finally:
        connection.close()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False
