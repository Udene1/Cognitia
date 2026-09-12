from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.learning import PersistentSolutionPatternLearner
from cognitia.memory import Experience, Outcome


def test_solution_knowledge_survives_a_new_store_instance(tmp_path) -> None:
    path = tmp_path / "knowledge.json"
    store = PersistentKnowledgeStore(path)
    learner = PersistentSolutionPatternLearner(store)

    experience = Experience(
        context={
            "solution_problem": "aggregate records by key",
            "solution_logic": (
                "partition records by key",
                "combine values within each partition",
                "return one result per key",
            ),
            "solution_implementation": "partition_then_reduce",
            "solution_language": "python",
        },
        action="implement aggregation",
        observation={"verified": True},
        outcome=Outcome("positive", "verified against expected totals"),
    )

    persisted = learner.learn_and_persist([experience])
    assert len(persisted) == 1

    fresh_store = PersistentKnowledgeStore(path)
    fresh_learner = PersistentSolutionPatternLearner(fresh_store)
    recovered = fresh_learner.candidates()

    assert len(recovered) == 1
    assert recovered[0].value["logic"] == (
        "partition records by key",
        "combine values within each partition",
        "return one result per key",
    )
    assert recovered[0].value["implementation"] == "partition_then_reduce"
