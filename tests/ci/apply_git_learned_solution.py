"""Recover a Git-derived solution in a fresh process and solve a new problem."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.learning.code_solutions import CodeSolutionLearner
from cognitia.learning.persistent_solutions import PersistentSolutionPatternLearner


KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_GIT_KNOWLEDGE", ".ci/git-cognitia-knowledge.json"))
PROBLEM = "Calculate the total spending for each customer from these orders."
ORDERS = [
    {"client": "Ada", "cost": 12},
    {"client": "Bola", "cost": 7},
    {"client": "Ada", "cost": 8},
    {"client": "Chidi", "cost": 10},
    {"client": "Bola", "cost": 3},
]


def execute_group_by_reduce(records: list[dict[str, object]]) -> dict[str, float]:
    """Execute the recovered family without the Git training schema."""
    if not records:
        return {}
    fields = tuple(records[0])
    key_fields = [field for field in fields if isinstance(records[0][field], str)]
    value_fields = [
        field for field in fields
        if isinstance(records[0][field], (int, float)) and not isinstance(records[0][field], bool)
    ]
    if len(key_fields) != 1 or len(value_fields) != 1:
        raise ValueError("expected one categorical key and one numeric value")

    key_field, value_field = key_fields[0], value_fields[0]
    totals: dict[str, float] = {}
    for record in records:
        key = str(record[key_field])
        totals[key] = totals.get(key, 0.0) + float(record[value_field])
    return totals


EXECUTORS = {"group_by_reduce": execute_group_by_reduce}


def main() -> None:
    # This is a new process. Only persisted knowledge is available; the Git
    # source is deliberately not loaded in this stage.
    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    persistent = PersistentSolutionPatternLearner(store)
    interpreter = CodeSolutionLearner()
    candidates = persistent.candidates(scope="git_source_learning")
    assert candidates, "fresh process must recover Git-derived knowledge"

    target_signature = interpreter.infer_problem_signature(PROBLEM)
    matching = [
        item for item in candidates
        if tuple(item.value["context"]["problem_signature"]) == target_signature
        and item.value["success_rate"] >= 1.0
    ]
    assert matching, "Cognitia must retrieve the Git-derived transferable pattern"

    selected = max(matching, key=lambda item: item.value["observations"])
    implementation = selected.value["implementation"]
    executor = EXECUTORS.get(implementation)
    assert executor is not None
    result = executor(ORDERS)
    expected = {"Ada": 20.0, "Bola": 10.0, "Chidi": 10.0}
    assert result == expected

    print(f"TARGET_SIGNATURE: {target_signature}")
    print(f"RECOVERED_IMPLEMENTATION: {implementation}")
    print(f"RESULT: {result}")
    print("GIT_DERIVED_TRANSFER_SUCCESS")


if __name__ == "__main__":
    main()
