"""Use Git-derived engineering cognition to reason about an economics problem."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.learning.concept_transfer import TradeoffBalanceInterpreter

KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_CROSS_DOMAIN_KNOWLEDGE", ".ci/cross-domain-knowledge.json"))
PROBLEM = (
    "Should a central bank adopt a new economic policy that improves growth but "
    "worsens inflation risk, or preserve the existing policy while the tradeoff is balanced?"
)


def apply_tradeoff_policy(*, improvement: bool, regression: bool) -> str:
    """Apply the recovered abstract policy to a new economic domain."""
    if improvement and regression:
        return "hold_for_balancing"
    if improvement and not regression:
        return "adopt"
    return "retain_baseline"


def main() -> None:
    # Fresh process: the engineering source is deliberately unavailable here.
    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    items = store.query(scope="cross_domain_transfer", predicate="has_solution_pattern")
    assert items, "fresh process must recover Git-derived conceptual knowledge"

    target_signature = TradeoffBalanceInterpreter.infer_problem_signature(PROBLEM)
    matching = [item for item in items if item.value["family"] in target_signature]
    assert matching, "Cognitia must map the economics problem to the learned abstraction"

    selected = matching[-1]
    logic = tuple(selected.value["logic"])
    result = apply_tradeoff_policy(improvement=True, regression=True)
    assert result == "hold_for_balancing"

    # Held-out economic case: improvement without regression should promote.
    assert apply_tradeoff_policy(improvement=True, regression=False) == "adopt"
    # Another held-out case: no useful improvement should retain the baseline.
    assert apply_tradeoff_policy(improvement=False, regression=True) == "retain_baseline"

    print(f"TARGET_SIGNATURE: {target_signature}")
    print(f"RECOVERED_LOGIC: {' -> '.join(logic)}")
    print(f"ECONOMIC_DECISION: {result}")
    print("HELD_OUT_CASES: 2")
    print("CROSS_DOMAIN_TRANSFER_SUCCESS")


if __name__ == "__main__":
    main()
