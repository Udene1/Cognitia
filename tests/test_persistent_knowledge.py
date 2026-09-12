from __future__ import annotations

import subprocess
from pathlib import Path

from cognitia.git_environment import GitRepositoryObserver
from cognitia.git_knowledge import GitKnowledgeIngestor
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.knowledge.persistent import PersistentKnowledgeStore


def _git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repo"
    repository.mkdir()
    _git(repository, "init", "-q")
    _git(repository, "config", "user.name", "Cognitia Test")
    _git(repository, "config", "user.email", "cognitia@example.test")
    (repository / "README.md").write_text("first\n", encoding="utf-8")
    _git(repository, "add", "README.md")
    _git(repository, "commit", "-m", "add initial knowledge")
    return repository


def test_persistent_store_survives_process_boundary(tmp_path: Path) -> None:
    path = tmp_path / "knowledge.json"
    item = KnowledgeItem(
        subject="commit-1",
        predicate="subject",
        value="add capability",
        source=KnowledgeSource(kind="git_commit", reference="git:test#commit-1"),
    )

    PersistentKnowledgeStore(path).add(item)

    restored = PersistentKnowledgeStore(path)
    assert restored.query(subject="commit-1", predicate="subject") == (item,)


def test_real_git_history_becomes_durable_knowledge(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    path = tmp_path / "knowledge.json"

    first_store = PersistentKnowledgeStore(path)
    observer = GitRepositoryObserver(repository)
    first_items = GitKnowledgeIngestor(first_store).ingest(observer)

    assert len(first_items) == 8
    assert {item.predicate for item in first_items} == {
        "repository",
        "author",
        "authored_at",
        "subject",
        "parent_ids",
        "files_changed",
        "insertions",
        "deletions",
    }
    commit_id = observer.head()
    assert all(item.subject == commit_id for item in first_items)
    assert all(item.scope == "repository_history" for item in first_items)
    assert all(item.source.kind == "git_commit" for item in first_items)

    # A new process/store instance sees the same knowledge and does not create
    # duplicates because knowledge IDs are deterministic for commit + predicate.
    second_store = PersistentKnowledgeStore(path)
    second_items = GitKnowledgeIngestor(second_store).ingest(observer)

    assert second_items == ()
    assert len(second_store.all()) == 8
