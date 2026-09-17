from pathlib import Path

from cognitia.environment import EnvironmentObservation
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


def test_environment_observation_can_be_archived_without_promotion(tmp_path: Path) -> None:
    path = tmp_path / "environment.sqlite"
    acquired = EnvironmentObservation(
        id="web:1",
        source="web:wikimedia:document",
        content="raw page content",
        reliability=0.7,
        metadata=(("url", "https://en.wikipedia.org/wiki/Example"), ("query", "example")),
    )

    with DurableEvidenceArchive(path) as archive:
        retained = archive.retain_environment(acquired)

    assert retained.kind == "environment_observation"
    assert retained.payload == acquired.content
    assert retained.environment == acquired.source
    assert ("query", "example") in retained.metadata
    assert ("reliability", "0.7") in retained.metadata


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
    digest = next(value for key, value in sample.observation.metadata if key == "sha256")
    assert len(digest) == 64
