"""CI stage 1: infer a solution from real source code and persist it."""
from __future__ import annotations

import json
import os
from pathlib import Path

from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.learning.code_solutions import CodeSolutionLearner
from cognitia.learning.persistent_solutions import PersistentSolutionPatternLearner


KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_KNOWLEDGE", ".ci/cognitia-knowledge.json"))

SOURCE = '''
def total_by_customer(purchases):
    totals = {}
    for purchase in purchases:
        customer = purchase["customer"]
        totals[customer] = totals.get(customer, 0) + purchase["amount"]
    return totals
'''


def main() -> None:
    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    code_learner = CodeSolutionLearner()
    solution_learner = PersistentSolutionPatternLearner(store)

    # The intended algorithm, logic, implementation label, and signature are
    # deliberately absent. Cognitia receives only a problem statement and the
    # executable program plus its observed successful outcome.
    experience = code_learner.experience(
        problem="sum purchase amounts by customer",
        source=SOURCE,
        outcome_kind="positive",
        outcome_description="held-out aggregation tests passed",
    )
    representation = code_learner.interpret(SOURCE)
    learned = solution_learner.learn_and_persist([experience])

    assert representation.algorithm_family == "group_by_reduce"
    assert learned, "stage 1 must persist an inferred solution"
    assert KNOWLEDGE_PATH.exists()

    payload = json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
    assert any(item["predicate"] == "has_solution_pattern" for item in payload)

    print("CODE_INFERENCE_SUCCESS")
    print(f"INFERRED_FAMILY: {representation.algorithm_family}")
    print(f"INFERRED_LOGIC: {' -> '.join(experience.context['solution_logic'])}")
    print("LEARNED_AND_PERSISTED")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
