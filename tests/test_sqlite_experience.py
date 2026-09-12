from datetime import datetime, timezone

from cognitia.memory.experience import Experience, Outcome
from cognitia.memory.sqlite import SQLiteExperienceStore


def test_sqlite_experience_survives_store_recreation(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    experience = Experience(
        context={"domain": "engineering", "candidate_gain": 0.2},
        action="hold_for_balancing",
        observation={"regression": 0.1},
        outcome=Outcome("positive", "candidate retained for repair", 1.0),
        occurred_at=datetime(2026, 9, 12, tzinfo=timezone.utc),
    )

    with SQLiteExperienceStore(path) as store:
        store.record(experience)

    with SQLiteExperienceStore(path) as reopened:
        recovered = reopened.all()

    assert recovered == (experience,)


def test_sqlite_experience_preserves_negative_consequences(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    experience = Experience(
        context={"domain": "test"},
        action="adopt_candidate",
        observation={"regression": 0.4},
        outcome=Outcome("negative", "protected capability regressed", 0.4),
    )

    with SQLiteExperienceStore(path) as store:
        store.record(experience)
        recovered = store.all()

    assert recovered[0].outcome.kind == "negative"
    assert recovered[0].outcome.description == "protected capability regressed"
