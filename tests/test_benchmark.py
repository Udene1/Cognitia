import pytest

from cognitia.benchmark import (
    BenchmarkCase,
    BenchmarkOutcome,
    BenchmarkSuite,
    compare_builds,
)


def test_benchmark_scores_weighted_passes() -> None:
    suite = BenchmarkSuite(
        name="arithmetic",
        capability="deterministic_reasoning",
        cases=(
            BenchmarkCase("easy", 2 + 2, 4, weight=1),
            BenchmarkCase("hard", 6 * 7, 42, weight=2),
        ),
    )

    result = suite.evaluate(
        "C0.1",
        lambda case: (
            __import__("cognitia.benchmark", fromlist=["CaseResult"]).CaseResult(
                case_id=case.id,
                outcome=BenchmarkOutcome.PASS,
                actual=case.expected,
            )
        ),
    )

    assert result.score == 1.0


def test_build_comparison_measures_growth() -> None:
    suite = BenchmarkSuite(
        name="reasoning",
        capability="hypothesis_testing",
        cases=(BenchmarkCase("case-1", "predict", "match"),),
    )

    def evaluate(outcome: BenchmarkOutcome, build: str):
        return suite.evaluate(
            build,
            lambda case: __import__("cognitia.benchmark", fromlist=["CaseResult"]).CaseResult(
                case_id=case.id,
                outcome=outcome,
            ),
        )

    baseline = evaluate(BenchmarkOutcome.FAIL, "C0.1")
    candidate = evaluate(BenchmarkOutcome.PASS, "C0.2")
    comparison = compare_builds(baseline, candidate)

    assert comparison.improvement == 1.0
    assert comparison.improved


def test_comparison_rejects_different_benchmarks() -> None:
    first = BenchmarkSuite(
        name="one",
        capability="x",
        cases=(BenchmarkCase("case", 1, 1),),
    ).evaluate(
        "C0.1",
        lambda case: __import__("cognitia.benchmark", fromlist=["CaseResult"]).CaseResult(
            case.id, BenchmarkOutcome.PASS
        ),
    )
    second = BenchmarkSuite(
        name="two",
        capability="x",
        cases=(BenchmarkCase("case", 1, 1),),
    ).evaluate(
        "C0.2",
        lambda case: __import__("cognitia.benchmark", fromlist=["CaseResult"]).CaseResult(
            case.id, BenchmarkOutcome.PASS
        ),
    )

    with pytest.raises(ValueError, match="same benchmark"):
        compare_builds(first, second)
