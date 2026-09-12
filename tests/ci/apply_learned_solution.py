"""CI stage 2: recover a solution in a fresh process and transfer it."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.learning.code_solutions import CodeSolutionLearner
from cognitia.learning.persistent_solutions import PersistentSolutionPatternLearner


KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_KNOWLEDGE", ".ci/cognitia-knowledge.json"))

PROBLEM = "Calculate total spending for each customer from a new set of purchases."
PURCHASES = [
    {"customer": "Ada", "amount": 12},
    {"customer": "Bola", "amount": 7},
    {"customer": "Ada", "amount": 8},
    {"customer": "Chidi", "amount": 10},
    {"customer": "Bola", "amount": 3},
]


def execute_group_by_reduce(records: list[dict[str, object]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for record in records:
        key = str(record["customer"])
        totals[key] = totals.get(key, 0) + int(record["amount"])
    return totals


EXECUTORS = {"group_by_reduce": execute_group_by_reduce}


def main() -> None:
    # Deliberately construct a fresh knowledge store in a new process. No stage-1
    # ExperienceStore is reused here.
    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    learner = PersistentSolutionPatternLearner(store)
    problem_interpreter = CodeSolutionLearner()
    candidates = learner.candidates()

    assert candidates, "stage 2 must recover knowledge persisted by stage 1"

    # Cognitia interprets the new problem itself. No structured signature is
    # supplied by the experiment author.
    target_signature = problem_interpreter.infer_problem_signature(PROBLEM)
    matching = [
        item
        for item in candidates
        if tuple(item.value["context"]["problem_signature"]) == target_signature
        and item.value["success_rate"] >= 1.0
    ]
    assert matching, "Cognitia must retrieve a successful transferable pattern"

    selected = max(matching, key=lambda item: item.value["observations"])
    logic = tuple(selected.value["logic"])
    implementation = selected.value["implementation"]
    executor = EXECUTORS.get(implementation)
    assert executor is not None, f"no executor registered for learned capability: {implementation}"

    result = executor(PURCHASES)
    expected = {"Ada": 20, "Bola": 10, "Chidi": 10}
    assert result == expected

    print(f"PROBLEM: {PROBLEM}")
    print(f"INFERRED_SIGNATURE: {target_signature}")
    print(f"RECOVERED_LOGIC: {' -> '.join(logic)}")
    print(f"RECOVERED_IMPLEMENTATION: {implementation}")
    print(f"RESULT: {result}")
    print("TRANSFER_SUCCESS")


if __name__ == "__main__":
    main()
