"""Learn a solution from Python source discovered through the Git environment."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.git_environment import GitRepositoryObserver
from cognitia.knowledge import PersistentKnowledgeStore
from cognitia.learning.code_solutions import CodeSolutionLearner
from cognitia.learning.persistent_solutions import PersistentSolutionPatternLearner


KNOWLEDGE_PATH = Path(os.environ.get("COGNITIA_CI_GIT_KNOWLEDGE", ".ci/git-cognitia-knowledge.json"))
REPOSITORY = Path(__file__).resolve().parents[2]
SOURCE_PATH = "tests/ci/git_source_case.py"
PROBLEM = "Compute total purchase value for every customer."


def main() -> None:
    observer = GitRepositoryObserver(REPOSITORY)
    sources = observer.python_sources(tracked_only=True)
    matches = [item for item in sources if item.path == SOURCE_PATH]
    assert len(matches) == 1, "the Git observer must discover the training source"

    source = matches[0].source
    learner = CodeSolutionLearner()
    experience = learner.experience(
        problem=PROBLEM,
        source=source,
        outcome_kind="positive",
        outcome_description="repository source executed successfully in its intended test",
        context={
            "environment": "git",
            "source_path": matches[0].path,
            "source_discovery": "GitRepositoryObserver.python_sources",
        },
    )

    store = PersistentKnowledgeStore(KNOWLEDGE_PATH)
    persistent = PersistentSolutionPatternLearner(store)
    learned = persistent.learn_and_persist([experience], scope="git_source_learning")
    assert learned

    representation = learner.interpret(source)
    assert representation.algorithm_family == "group_by_reduce"

    print(f"GIT_HEAD: {observer.head()}")
    print(f"SOURCE_DISCOVERED: {matches[0].path}")
    print(f"SOURCE_DISCOVERY_PATH: GitRepositoryObserver.python_sources")
    print(f"INFERRED_FAMILY: {representation.algorithm_family}")
    print(f"INFERRED_LOGIC: {' -> '.join(experience.context['solution_logic'])}")
    print("GIT_SOURCE_LEARNING_SUCCESS")


if __name__ == "__main__":
    main()
