"""Local Git repositories as an environment Cognitia can observe.

Git is treated as an evidence source, not as a reasoning engine. The observer
extracts repository history into structured engineering events; Cognitia's
existing experience memory remains responsible for retaining those observations.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import subprocess
from typing import Sequence

from .engineering import EngineeringEvent, EngineeringExperienceRecorder
from .memory.experience import Experience, Outcome


class GitEnvironmentError(RuntimeError):
    """Raised when a repository cannot be observed safely."""


@dataclass(frozen=True)
class GitCommitObservation:
    """Structured observation of one commit in a local Git repository."""

    commit_id: str
    parent_ids: tuple[str, ...]
    author: str
    authored_at: datetime
    subject: str
    files_changed: int
    insertions: int
    deletions: int


class GitRepositoryObserver:
    """Read-only observer for a local Git working tree."""

    def __init__(self, repository: str | Path) -> None:
        self.repository = Path(repository).expanduser().resolve()

    def _run(self, args: Sequence[str]) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.repository,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise GitEnvironmentError("git executable is not available") from exc
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout).strip()
            raise GitEnvironmentError(detail or "git observation failed") from exc
        return result.stdout

    def head(self) -> str:
        """Return the current commit at HEAD."""
        return self._run(["rev-parse", "HEAD"]).strip()

    def commits(self, limit: int | None = None) -> tuple[GitCommitObservation, ...]:
        """Observe commit history without modifying the repository."""
        if limit is not None and limit < 1:
            raise ValueError("limit must be positive")

        args = [
            "log",
            "--date=iso-strict",
            "--format=%H%x1f%P%x1f%an%x1f%aI%x1f%s%x1e",
            "--shortstat",
        ]
        if limit is not None:
            args.append(f"-n{limit}")
        output = self._run(args)
        observations: list[GitCommitObservation] = []
        for record in output.split("\x1e"):
            if not record.strip():
                continue
            lines = [line for line in record.splitlines() if line.strip()]
            if not lines:
                continue
            fields = lines[0].split("\x1f")
            if len(fields) != 5:
                raise GitEnvironmentError("unexpected git log record")
            stats = lines[1] if len(lines) > 1 else ""
            observations.append(
                GitCommitObservation(
                    commit_id=fields[0],
                    parent_ids=tuple(fields[1].split()) if fields[1] else (),
                    author=fields[2],
                    authored_at=datetime.fromisoformat(fields[3]),
                    subject=fields[4],
                    files_changed=_stat_value(stats, r"file(?:s)? changed"),
                    insertions=_stat_value(stats, r"insertion(?:s)?"),
                    deletions=_stat_value(stats, r"deletion(?:s)?"),
                )
            )
        return tuple(observations)


def _stat_value(stats: str, label_pattern: str) -> int:
    match = re.search(rf"(\d+)\s+{label_pattern}", stats)
    return int(match.group(1)) if match else 0


class GitHistoryIngestor:
    """Turn observed Git history into canonical engineering experiences."""

    def __init__(self, recorder: EngineeringExperienceRecorder) -> None:
        self._recorder = recorder
        self._ingested: set[str] = set()

    def ingest(
        self,
        observer: GitRepositoryObserver,
        *,
        limit: int | None = None,
    ) -> tuple[Experience, ...]:
        """Record previously unseen commits as neutral observations.

        A commit is not assumed to be good merely because it exists. Its initial
        epistemic outcome is neutral; later test, benchmark, regression, or repair
        observations can establish what the change actually accomplished.
        """
        experiences: list[Experience] = []
        for commit in observer.commits(limit):
            if commit.commit_id in self._ingested:
                continue
            event = EngineeringEvent(
                kind="git_commit",
                context={
                    "repository": str(observer.repository),
                    "commit_id": commit.commit_id,
                    "parents": commit.parent_ids,
                    "author": commit.author,
                },
                action=f"commit: {commit.subject}",
                observation={
                    "subject": commit.subject,
                    "files_changed": commit.files_changed,
                    "insertions": commit.insertions,
                    "deletions": commit.deletions,
                },
                outcome=Outcome(
                    "neutral",
                    "commit observed; effectiveness requires subsequent evidence",
                ),
                occurred_at=commit.authored_at,
            )
            experiences.append(self._recorder.record(event))
            self._ingested.add(commit.commit_id)
        return tuple(experiences)

    def ingested_commit_ids(self) -> frozenset[str]:
        """Return commit IDs already converted into experiences by this ingestor."""
        return frozenset(self._ingested)
