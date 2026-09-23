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


def test_sqlite_observation_is_idempotent_and_rejects_identity_collisions(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    observation = Observation.create(
        environment="cashflow-os", kind="lead.state", subject="lead-1", payload="raw record"
    )

    with SQLiteObservationStore(path) as store:
        store.ingest(observation)
        store.ingest(observation)
        assert store.all() == (observation,)

        collision = Observation(
            id=observation.id,
            environment=observation.environment,
            kind=observation.kind,
            subject=observation.subject,
            payload="different raw record",
        )
        try:
            store.ingest(collision)
        except ValueError as error:
            assert str(observation.id) in str(error)
        else:
            raise AssertionError("expected observation identity collision to fail")


def test_latest_observed_at_is_recovered_from_durable_ledger(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    older = Observation.create(
        environment="cashflow-os",
        kind="activity.note",
        subject="older",
        payload="older",
        observed_at="2026-09-22T12:00:00.000Z",
    )
    newer = Observation.create(
        environment="cashflow-os",
        kind="activity.note",
        subject="newer",
        payload="newer",
        observed_at="2026-09-22T12:05:00.000Z",
    )

    with SQLiteObservationStore(path) as store:
        store.ingest(newer)
        store.ingest(older)
        assert store.latest_observed_at(environment="cashflow-os") == "2026-09-22T12:05:00.000Z"
        assert store.latest_observed_at(environment="missing") is None
