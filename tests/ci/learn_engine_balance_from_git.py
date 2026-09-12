"""Learn an engineering tradeoff policy from source discovered through Git."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.git_environment import GitRepositoryObserver
from cognitia.knowledge import KnowledgeItem, KnowledgeSource, PersistentKnowledgeStore
from cognitia.learning.concept_transfer import TradeoffBalanceInterpreter

KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_CROSS_DOMAIN_KNOWLEDGE", ".ci/cross-domain-knowledge.json"))
REPOSITORY = Path(__file__).resolve().parents[2]
SOURCE_PATH = "tests/ci/engine_balance_case.py"


def main() -> None:
    observer = GitRepositoryObserver(REPOSITORY)
    sources = observer.python_sources(tracked_only=True)
    matches = [item for item in sources if item.path == SOURCE_PATH]
    assert len(matches) == 1

    representation = TradeoffBalanceInterpreter().interpret(matches[0].source)
    assert representation.family == "tradeoff_balance"

    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    store.add(KnowledgeItem(
        subject="engineering capability regression balancing",
        predicate="has_solution_pattern",
        value={
            "family": representation.family,
            "logic": representation.logic,
            "confidence": representation.confidence,
            "source_path": matches[0].path,
            "source_discovery": "GitRepositoryObserver.python_sources",
        },
        source=KnowledgeSource(
            kind="git_source",
            reference=f"{observer.head()}:{matches[0].path}",
            reliability=1.0,
        ),
        scope="cross_domain_transfer",
    ))

    print(f"SOURCE_DISCOVERED: {matches[0].path}")
    print("SOURCE_DISCOVERY_PATH: GitRepositoryObserver.python_sources")
    print(f"INFERRED_FAMILY: {representation.family}")
    print(f"INFERRED_LOGIC: {' -> '.join(representation.logic)}")
    print("CROSS_DOMAIN_CONCEPT_LEARNED")


if __name__ == "__main__":
    main()
