"""CI stage 2: start a fresh process and solve a new problem from persisted knowledge."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.learning import PersistentSolutionPatternLearner


KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_KNOWLEDGE", ".ci/cognitia-knowledge.json"))


PROBLEM = "Calculate total spending for each customer from a new set of purchases."
PURCHASES = [
    {"customer": "Ada", "amount": 12},
    {"customer": "Bola", "amount": 7},
    {"customer": "Ada", "amount": 8},
    {"customer": "Chidi", "amount": 10},
    {"customer": "Bola", "amount": 3},
]


def execute_partition_then_reduce(records: list[dict[str, object]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for record in records:
        key = str(record["customer"])
        totals[key] = totals.get(key, 0) + int(record["amount"])
    return totals


def main() -> None:
    # Deliberately construct a fresh knowledge store in a new process. No stage-1
    # ExperienceStore is reused here.
    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    learner = PersistentSolutionPatternLearner(store)
    candidates = learner.candidates()

    assert candidates, "stage 2 must recover knowledge persisted by stage 1"

    # The target problem is phrased differently from the training problem.
    # Cognitia is given the problem class, not the implementation.
    matching = [
        item
        for item in candidates
        if item.subject == "aggregate records by key"
        and item.value["success_rate"] >= 1.0
    ]
    assert matching, "Cognitia must retrieve a successful transferable pattern"

    selected = max(matching, key=lambda item: item.value["observations"])
    logic = tuple(selected.value["logic"])
    implementation = selected.value["implementation"]

    assert logic == (
        "partition records by key",
        "combine values within each partition",
        "return one result per key",
    )
    assert implementation == "partition_then_reduce"

    # Execute the computational pattern against a genuinely different dataset.
    result = execute_partition_then_reduce(PURCHASES)
    expected = {"Ada": 20, "Bola": 10, "Chidi": 10}
    assert result == expected

    print(f"PROBLEM: {PROBLEM}")
    print(f"RECOVERED_LOGIC: {' -> '.join(logic)}")
    print(f"RECOVERED_IMPLEMENTATION: {implementation}")
    print(f"RESULT: {result}")
    print("TRANSFER_SUCCESS")


if __name__ == "__main__":
    main()
