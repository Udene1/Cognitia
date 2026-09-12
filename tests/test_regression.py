import pytest

from cognitia.benchmark import BenchmarkCase, BenchmarkOutcome, BenchmarkSuite, CaseResult
from cognitia.regression import RegressionPolicy, evaluate_promotion


def result(suite: BenchmarkSuite, build: str, outcome: BenchmarkOutcome):
    return suite.evaluate(
        build,
        lambda case: CaseResult(case.id, outcome),
    )


def test_promotion_allows_improvement_without_regression() -> None:
    target = BenchmarkSuite("causal", "causal_reasoning", (BenchmarkCase("a", 1, 1),))
    protected = BenchmarkSuite("math", "deterministic_reasoning", (BenchmarkCase("a", 1, 1),))

    decision = evaluate_promotion(
        result(target, "C0.1", BenchmarkOutcome.FAIL),
        result(target, "C0.2", BenchmarkOutcome.PASS),
        (result(protected, "C0.1", BenchmarkOutcome.PASS),),
        (result(protected, "C0.2", BenchmarkOutcome.PASS),),
    )

    assert decision.eligible
    assert decision.primary.improvement == 1.0
    assert decision.findings[0].regression == 0.0


def test_promotion_rejects_regression() -> None:
    target = BenchmarkSuite("causal", "causal_reasoning", (BenchmarkCase("a", 1, 1),))
    protected = BenchmarkSuite("math", "deterministic_reasoning", (BenchmarkCase("a", 1, 1),))

    decision = evaluate_promotion(
        result(target, "C0.1", BenchmarkOutcome.FAIL),
        result(target, "C0.2", BenchmarkOutcome.PASS),
        (result(protected, "C0.1", BenchmarkOutcome.PASS),),
        (result(protected, "C0.2", BenchmarkOutcome.FAIL),),
    )

    assert not decision.eligible
    assert decision.findings[0].regression == 1.0
    assert "regresses" in decision.reason


def test_policy_can_allow_small_regression() -> None:
    target = BenchmarkSuite("target", "new_capability", (BenchmarkCase("a", 1, 1),))
    protected = BenchmarkSuite("protected", "old_capability", (BenchmarkCase("a", 1, 1),))

    decision = evaluate_promotion(
        result(target, "C0.1", BenchmarkOutcome.FAIL),
        result(target, "C0.2", BenchmarkOutcome.PASS),
        (result(protected, "C0.1", BenchmarkOutcome.PASS),),
        (result(protected, "C0.2", BenchmarkOutcome.FAIL),),
        RegressionPolicy(max_regression=1.0),
    )

    assert decision.eligible


def test_protected_benchmark_count_must_match() -> None:
    target = BenchmarkSuite("target", "new", (BenchmarkCase("a", 1, 1),))
    protected = BenchmarkSuite("protected", "old", (BenchmarkCase("a", 1, 1),))

    with pytest.raises(ValueError, match="equal length"):
        evaluate_promotion(
            result(target, "C0.1", BenchmarkOutcome.FAIL),
            result(target, "C0.2", BenchmarkOutcome.PASS),
            (result(protected, "C0.1", BenchmarkOutcome.PASS),),
            (),
        )
