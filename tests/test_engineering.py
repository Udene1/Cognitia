from cognitia.engineering import EngineeringEvent, EngineeringExperienceRecorder
from cognitia.memory.experience import ExperienceStore, Outcome


def test_engineering_event_becomes_canonical_experience():
    event = EngineeringEvent(
        kind="regression_repair",
        context={"capability": "new_reasoning_method"},
        action="construct bounded repair candidate",
        observation={"regression": 0.0, "new_capability_gain": 0.2},
        outcome=Outcome("positive", "repair preserved the protected baseline"),
    )

    experience = event.to_experience()

    assert experience.context["environment"] == "engineering"
    assert experience.context["event_kind"] == "regression_repair"
    assert experience.context["capability"] == "new_reasoning_method"
    assert experience.action == "construct bounded repair candidate"
    assert experience.observation["regression"] == 0.0
    assert experience.outcome.kind == "positive"


def test_recorder_uses_existing_append_only_experience_store():
    store = ExperienceStore()
    recorder = EngineeringExperienceRecorder(store)

    first = recorder.record_outcome(
        kind="implementation",
        context={"file": "cognitia/engineering.py"},
        action="add engineering event ingestion",
        observation={"tests": "not_run"},
        outcome=Outcome("neutral", "implementation recorded before validation"),
    )
    second = recorder.record(
        EngineeringEvent(
            kind="validation",
            context={"file": "tests/test_engineering.py"},
            action="add ingestion tests",
            observation={"test_count": 2},
            outcome=Outcome("positive", "invariants are covered"),
        )
    )

    assert store.all() == (first, second)
    assert first.context["environment"] == "engineering"
    assert second.context["environment"] == "engineering"


def test_engineering_event_does_not_turn_an_attempt_into_success():
    event = EngineeringEvent(
        kind="experiment",
        context={"hypothesis": "repair will remove regression"},
        action="run repair candidate",
        observation={"regression": 0.1},
        outcome=Outcome("negative", "candidate still regressed protected capability"),
    )

    experience = event.to_experience()

    assert experience.outcome.kind == "negative"
    assert experience.observation["regression"] == 0.1
