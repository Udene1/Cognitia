"""CI stage 1: learn a computational solution and persist it to disk."""
from __future__ import annotations

import json
import os
from pathlib import Path

from cognitia.learning import PersistentSolutionPatternLearner
from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.memory import Experience, Outcome


KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_KNOWLEDGE", ".ci/cognitia-knowledge.json"))


def main() -> None:
    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    learner = PersistentSolutionPatternLearner(store)

    experiences = [
        Experience(
            context={
                "solution_problem": "aggregate records by key",
                "solution_logic": (
                    "partition records by key",
                    "combine values within each partition",
                    "return one result per key",
                ),
                "solution_implementation": "partition_then_reduce",
                "solution_language": "python",
                "data_shape": "batch",
            },
            action="implement transaction aggregation",
            observation={"tests_passed": True},
            outcome=Outcome("positive", "aggregation tests passed"),
        ),
        Experience(
            context={
                "solution_problem": "aggregate records by key",
                "solution_logic": (
                    "partition records by key",
                    "combine values within each partition",
                    "return one result per key",
                ),
                "solution_implementation": "partition_then_reduce",
                "solution_language": "python",
                "data_shape": "batch",
            },
            action="implement transaction aggregation",
            observation={"tests_passed": True},
            outcome=Outcome("positive", "aggregation benchmark passed"),
        ),
    ]

    learned = learner.learn_and_persist(experiences)
    assert learned, "stage 1 must persist at least one learned solution"
    assert KNOWLEDGE_PATH.exists()

    payload = json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
    assert any(item["predicate"] == "has_solution_pattern" for item in payload)

    print("LEARNED_AND_PERSISTED")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
