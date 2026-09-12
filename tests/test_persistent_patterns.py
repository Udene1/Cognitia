from cognitia.knowledge.persistent import PersistentKnowledgeStore
from cognitia.learning import PersistentPatternLearner
from cognitia.memory import Experience, Outcome


def make_experience(outcome: str, *, commit_id: str) -> Experience:
    return Experience(
        context={
            "environment": "engineering",
            "event_kind": "capability_integration",
            "commit_id": commit_id,
        },
        action="retain_capability_and_repair_regression",
        observation={"commit_id": commit_id},
        outcome=Outcome(kind=outcome, description=outcome),
    )


def test_learned_pattern_persists_without_volatile_commit_identity(tmp_path) -> None:
    path = tmp_path / "knowledge.json"
    store = PersistentKnowledgeStore(path)
    learner = PersistentPatternLearner(store)

    items = learner.learn_and_persist(
        [
            make_experience("positive", commit_id="a"),
            make_experience("positive", commit_id="b"),
            make_experience("negative", commit_id="c"),
        ],
        context_keys=("environment", "event_kind"),
    )

    assert len(items) == 1
    assert items[0].value["positive"] == 2
    assert items[0].value["negative"] == 1
    assert items[0].value["observations"] == 3
    assert items[0].value["success_rate"] == 2 / 3

    restarted = PersistentKnowledgeStore(path)
    restored = restarted.query(scope="learned_patterns")
    assert len(restored) == 1
    assert restored[0].value == items[0].value


def test_relearning_same_experiences_is_idempotent(tmp_path) -> None:
    store = PersistentKnowledgeStore(tmp_path / "knowledge.json")
    learner = PersistentPatternLearner(store)
    experiences = [make_experience("positive", commit_id="a")]

    first = learner.learn_and_persist(
        experiences,
        context_keys=("environment", "event_kind"),
    )
    second = learner.learn_and_persist(
        experiences,
        context_keys=("environment", "event_kind"),
    )

    assert len(first) == 1
    assert second == ()
    assert len(store.query(scope="learned_patterns")) == 1
