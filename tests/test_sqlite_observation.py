from cognitia.memory.observation_sqlite import SQLiteObservationStore
from cognitia.observation import Observation


def test_sqlite_observation_survives_store_recreation(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    observation = Observation.create(
        environment="git",
        kind="commit",
        subject="abc123",
        payload="changed worker fencing",
        source_uri="git://Cognitia@abc123",
        parent_ids=("parent1",),
        metadata=(("files", "3"),),
    )

    with SQLiteObservationStore(path) as store:
        store.ingest(observation)

    with SQLiteObservationStore(path) as reopened:
        assert reopened.get(observation.id) == observation
        assert reopened.by_environment("git") == (observation,)


def test_observation_can_be_retained_without_becoming_knowledge(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    observation = Observation.create(
        environment="git", kind="commit", subject="def456", payload="a failed attempt"
    )
    with SQLiteObservationStore(path) as store:
        store.ingest(observation)
        assert store.all() == (observation,)
