from cognitia.learning import ConditionalPatternLearner
from cognitia.memory import Experience, Outcome


def experience(context: dict[str, object], outcome: str) -> Experience:
    return Experience(
        context=context,
        action="restart_worker",
        observation={},
        outcome=Outcome(kind=outcome, description=outcome),
    )


def test_same_action_can_have_different_contextual_outcomes() -> None:
    experiences = [
        experience({"cause": "memory_pressure"}, "positive"),
        experience({"cause": "database_lock"}, "negative"),
    ]

    patterns = ConditionalPatternLearner().learn(experiences)

    assert len(patterns) == 2
    memory_pattern = next(p for p in patterns if p.context == (("cause", "memory_pressure"),))
    lock_pattern = next(p for p in patterns if p.context == (("cause", "database_lock"),))

    assert memory_pattern.success_rate == 1.0
    assert lock_pattern.success_rate == 0.0


def test_applicable_pattern_is_conditioned_on_current_context() -> None:
    experiences = [
        experience({"cause": "memory_pressure"}, "positive"),
        experience({"cause": "database_lock"}, "negative"),
    ]

    learner = ConditionalPatternLearner()

    applicable = learner.applicable(
        experiences,
        action="restart_worker",
        context={"cause": "database_lock", "region": "eu"},
    )

    assert len(applicable) == 1
    assert applicable[0].negative == 1
    assert applicable[0].positive == 0
