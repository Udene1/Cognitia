from datetime import datetime, timezone

from cognitia.durable import DurableEvent, SQLiteCognitiveJournal


def test_event_survives_store_recreation(tmp_path):
    path = tmp_path / "cognition.sqlite"
    event = DurableEvent(
        kind="hypothesis_revision",
        source="engineering:test",
        payload={
            "hypothesis_id": "h-1",
            "old_confidence": 0.8,
            "new_confidence": 0.6,
            "reason": "held-out contradiction",
        },
        occurred_at=datetime(2026, 9, 12, tzinfo=timezone.utc),
    )

    with SQLiteCognitiveJournal(path) as journal:
        journal.append(event)

    with SQLiteCognitiveJournal(path) as reopened:
        recovered = reopened.all()
        by_kind = reopened.by_kind("hypothesis_revision")

    assert recovered == (event,)
    assert by_kind == (event,)


def test_append_many_is_atomic_for_serializable_events(tmp_path):
    path = tmp_path / "cognition.sqlite"
    events = tuple(
        DurableEvent(kind="observation", source="test", payload={"index": i})
        for i in range(3)
    )

    with SQLiteCognitiveJournal(path) as journal:
        assert journal.append_many(events) == events
        assert journal.all() == events
