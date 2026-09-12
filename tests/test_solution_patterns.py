from cognitia.learning import SolutionPatternLearner
from cognitia.memory import Experience, Outcome


def experience(
    *,
    outcome: str,
    implementation: str = "partition_then_reduce",
    language: str = "python",
    context: dict[str, object] | None = None,
) -> Experience:
    return Experience(
        context={
            **(context or {}),
            "solution_problem": "aggregate records by key",
            "solution_logic": (
                "partition records by key",
                "combine values within each partition",
                "return one result per key",
            ),
            "solution_implementation": implementation,
            "solution_language": language,
        },
        action="implement aggregation",
        observation={"tests_passed": outcome == "positive"},
        outcome=Outcome(outcome, f"{outcome} implementation result"),
    )


def test_learns_concrete_code_and_its_abstract_logic_together() -> None:
    pattern = SolutionPatternLearner().learn([experience(outcome="positive")])[0]

    assert pattern.problem == "aggregate records by key"
    assert pattern.logic == (
        "partition records by key",
        "combine values within each partition",
        "return one result per key",
    )
    assert pattern.implementation == "partition_then_reduce"
    assert pattern.language == "python"
    assert pattern.success_rate == 1.0


def test_code_learning_preserves_negative_and_neutral_evidence() -> None:
    learner = SolutionPatternLearner()
    pattern = learner.learn(
        [
            experience(outcome="positive"),
            experience(outcome="negative"),
            experience(outcome="neutral"),
        ]
    )[0]

    assert pattern.positive == 1
    assert pattern.negative == 1
    assert pattern.neutral == 1
    assert pattern.observations == 3


def test_different_implementations_remain_distinct_solutions() -> None:
    patterns = SolutionPatternLearner().learn(
        [
            experience(outcome="positive", implementation="partition_then_reduce"),
            experience(outcome="positive", implementation="sort_then_scan"),
        ]
    )

    assert {pattern.implementation for pattern in patterns} == {
        "partition_then_reduce",
        "sort_then_scan",
    }


def test_applicable_returns_solution_for_matching_context() -> None:
    learner = SolutionPatternLearner()
    experiences = [
        experience(outcome="positive", context={"data_shape": "batch"}),
        experience(outcome="positive", context={"data_shape": "stream"}),
    ]

    matches = learner.applicable(
        experiences,
        problem="aggregate records by key",
        context={"data_shape": "stream"},
    )

    assert len(matches) == 1
    assert matches[0].context == (("data_shape", "stream"),)


def test_unannotated_experience_does_not_become_code_knowledge() -> None:
    raw = Experience(
        context={"repository": "Cognitia", "commit": "implement grouping"},
        action="write code",
        observation={"files_changed": 2},
        outcome=Outcome("positive", "tests passed"),
    )

    assert SolutionPatternLearner().learn([raw]) == ()
