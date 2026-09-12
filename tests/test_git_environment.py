from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from cognitia.engineering import EngineeringExperienceRecorder
from cognitia.git_environment import GitEnvironmentError, GitHistoryIngestor, GitRepositoryObserver
from cognitia.memory.experience import ExperienceStore


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Cognitia Test")
    _git(repo, "config", "user.email", "cognitia@example.test")
    (repo / "one.txt").write_text("one\n")
    _git(repo, "add", "one.txt")
    _git(repo, "commit", "-m", "first observation")
    (repo / "one.txt").write_text("one\ntwo\n")
    (repo / "two.txt").write_text("two\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "second observation")
    return repo


def test_observer_reads_real_git_history(tmp_path: Path):
    repo = _repository(tmp_path)
    observations = GitRepositoryObserver(repo).commits()
    assert len(observations) == 2
    assert observations[0].subject == "second observation"
    assert observations[0].files_changed == 2
    assert observations[0].insertions == 2
    assert observations[0].deletions == 0
    assert observations[1].parent_ids == ()
    assert GitRepositoryObserver(repo).head() == observations[0].commit_id


def test_observer_discovers_python_source_as_environment_evidence(tmp_path: Path):
    repo = _repository(tmp_path)
    source = "def total(values):\n    return sum(values)\n"
    (repo / "solver.py").write_text(source)
    _git(repo, "add", "solver.py")
    _git(repo, "commit", "-m", "add solver")

    observations = GitRepositoryObserver(repo).python_sources()

    solver = next(item for item in observations if item.path == "solver.py")
    assert solver.language == "python"
    assert solver.source == source


def test_ingestor_records_commits_as_neutral_experiences(tmp_path: Path):
    repo = _repository(tmp_path)
    store = ExperienceStore()
    ingestor = GitHistoryIngestor(EngineeringExperienceRecorder(store))
    first = ingestor.ingest(GitRepositoryObserver(repo))
    second = ingestor.ingest(GitRepositoryObserver(repo))
    assert len(first) == 2
    assert second == ()
    assert len(store.all()) == 2
    assert all(experience.context["environment"] == "engineering" for experience in first)
    assert all(experience.context["event_kind"] == "git_commit" for experience in first)
    assert all(experience.outcome.kind == "neutral" for experience in first)
    assert ingestor.ingested_commit_ids() == frozenset(experience.context["commit_id"] for experience in first)


def test_observer_rejects_non_repository(tmp_path: Path):
    with pytest.raises(GitEnvironmentError):
        GitRepositoryObserver(tmp_path / "missing").head()


def test_invalid_commit_limit_is_rejected(tmp_path: Path):
    repo = _repository(tmp_path)
    with pytest.raises(ValueError):
        GitRepositoryObserver(repo).commits(limit=0)
