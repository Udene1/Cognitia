from cognitia.knowledge import KnowledgeSource, SQLiteKnowledgeStore
from cognitia.knowledge.model import KnowledgeItem
from cognitia.learning.persistent_patterns import PersistentPatternLearner
from cognitia.learning.persistent_solutions import PersistentSolutionPatternLearner
from cognitia.memory import Experience, Outcome


def experience(*, positive: bool, strategy: str = "balanced_route") -> Experience:
    return Experience(
        context={
            "reasoning_strategy": strategy,
            "solution_problem": "aggregate by customer",
            "solution_logic": ["group records", "combine values", "emit totals"],
            "solution_implementation": "group_by_reduce",
            "solution_language": "python",
        },
        action=strategy,
        observation={"verified": positive},
        outcome=Outcome("positive" if positive else "negative", "held-out test"),
    )


def test_solution_patterns_survive_sqlite_reopen(tmp_path):
    path = tmp_path / "memory.sqlite"
    with SQLiteKnowledgeStore(path) as store:
        learner = PersistentSolutionPatternLearner(store)
        learned = learner.learn_and_persist([experience(positive=True)])
        assert len(learned) == 1

    with SQLiteKnowledgeStore(path) as reopened:
        candidates = PersistentSolutionPatternLearner(reopened).candidates()
        assert len(candidates) == 1
        assert candidates[0].value["logic"] == ["group records", "combine values", "emit totals"]
        assert candidates[0].source.kind == "solution_learning"


def test_contextual_patterns_use_same_durable_backend(tmp_path):
    path = tmp_path / "memory.sqlite"
    with SQLiteKnowledgeStore(path) as store:
        learner = PersistentPatternLearner(store)
        items = learner.learn_and_persist(
            [experience(positive=True), experience(positive=True)],
            context_keys=("reasoning_strategy",),
        )
        assert len(items) == 1

    with SQLiteKnowledgeStore(path) as reopened:
        rows = reopened.query(predicate="performed_as_pattern", scope="learned_patterns")
        assert len(rows) == 1
        assert rows[0].value["success_rate"] == 1.0


def test_knowledge_provenance_round_trips_without_loss(tmp_path):
    path = tmp_path / "knowledge.sqlite"
    item = KnowledgeItem(
        id="known-1",
        subject="postgres",
        predicate="has_observation",
        value={"cpu": 94, "tags": ["production", "database"]},
        source=KnowledgeSource(kind="monitor", reference="db://primary", reliability=0.93),
        scope="engineering",
    )
    with SQLiteKnowledgeStore(path) as store:
        store.add(item)
    with SQLiteKnowledgeStore(path) as reopened:
        assert reopened.all() == (item,)
