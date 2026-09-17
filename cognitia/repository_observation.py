"""Observe repository source as evidence with commit identity and provenance.

This is intentionally an observation boundary, not a code-learning system. It
exposes source artifacts and repository state so downstream cognition can decide
what, if anything, the evidence means.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import subprocess

from .observation import Observation


@dataclass(frozen=True)
class RepositorySourceObservation:
    observation: Observation
    commit: str
    path: str
    language: str


class GitRepositoryObserver:
    """Read tracked repository source without assigning semantic meaning."""

    def __init__(self, repository: str | Path = ".") -> None:
        self.repository = Path(repository)

    def commit(self) -> str:
        return self._git("rev-parse", "HEAD")

    def tracked_files(self) -> tuple[str, ...]:
        output = self._git("ls-files", "-z")
        return tuple(item for item in output.split("\0") if item)

    def python_sources(self) -> tuple[RepositorySourceObservation, ...]:
        return self.sources(suffixes=(".py",))

    def sources(self, *, suffixes: tuple[str, ...] = (".py",)) -> tuple[RepositorySourceObservation, ...]:
        commit = self.commit()
        result: list[RepositorySourceObservation] = []
        for relative in self.tracked_files():
            if not relative.endswith(suffixes):
                continue
            path = self.repository / relative
            payload = path.read_text(encoding="utf-8")
            language = _language_for(relative)
            digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            observation = Observation.create(
                environment="git",
                kind="repository_source",
                subject=relative,
                payload=payload,
                source_uri=f"git:{commit}:{relative}",
                metadata=(
                    ("commit", commit),
                    ("path", relative),
                    ("language", language),
                    ("sha256", digest),
                ),
            )
            result.append(RepositorySourceObservation(observation, commit, relative, language))
        return tuple(result)

    def observe_commit(self) -> Observation:
        commit = self.commit()
        files = self.tracked_files()
        manifest = "\n".join(files)
        return Observation.create(
            environment="git",
            kind="repository_state",
            subject=commit,
            payload=manifest,
            source_uri=f"git:{commit}",
            metadata=(("commit", commit), ("tracked_file_count", str(len(files)))),
        )

    def _git(self, *args: str) -> str:
        completed = subprocess.run(
            ("git", *args),
            cwd=self.repository,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip("\n")


def _language_for(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {".py": "python", ".js": "javascript", ".ts": "typescript", ".go": "go", ".rs": "rust"}.get(suffix, suffix.lstrip("."))
