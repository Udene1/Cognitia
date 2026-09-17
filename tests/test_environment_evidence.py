from pathlib import Path

from cognitia.evidence_archive import DurableEvidenceArchive
from cognitia.observation import Observation
from cognitia.repository_observation import GitRepositoryObserver


def test_raw_observation_survives_process_restart(tmp_path: Path) -> None:
    path = tmp_path / "evidence.sqlite"
    observation = Observation.create(
        environment="web",
        kind="document",
        subject="example",
        payload="raw source evidence",
        source_uri="https://example.invalid/source",
        metadata=(("query", "example"),),
    )

    with DurableEvidenceArchive(path) as archive:
        archive.retain(observation)

    with DurableEvidenceArchive(path) as restarted:
        restored = restarted.get(observation.id)

    assert restored == observation


def test_repository_observer_retains_commit_and_source_provenance() -> None:
    observer = GitRepositoryObserver(".")
    state = observer.observe_commit()
    sources = observer.python_sources()

    assert state.environment == "git"
    assert state.kind == "repository_state"
    assert state.subject == observer.commit()
    assert state.source_uri == f"git:{observer.commit()}"
    assert sources
    sample = sources[0]
    assert sample.commit == observer.commit()
    assert sample.observation.kind == "repository_source"
    assert sample.observation.source_uri == f"git:{sample.commit}:{sample.path}"
    assert ("commit", sample.commit) in sample.observation.metadata
    assert ("path", sample.path) in sample.observation.metadata
    assert ("sha256", next(value for key, value in sample.observation.metadata if key == "sha256"))
