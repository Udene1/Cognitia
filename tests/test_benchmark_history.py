from cognitia.benchmark import BenchmarkOutcome, BenchmarkResult, CaseResult
from cognitia.benchmark_history import BenchmarkHistory, EvaluationRecord


def result(build: str) -> BenchmarkResult:
    return BenchmarkResult(
        benchmark="b1", capability="c1", build=build,
        cases=(CaseResult("case", BenchmarkOutcome.PASS, actual=1),), score=1.0,
    )


def test_history_retains_multiple_evaluations_for_same_candidate():
    history = BenchmarkHistory()
    history.record(EvaluationRecord("candidate", "build-1", result("build-1"), ()))
    history.record(EvaluationRecord("candidate", "build-2", result("build-2"), (), disposition="held"))

    assert len(history.for_candidate("candidate")) == 2
    assert history.latest("candidate").candidate_build == "build-2"
    assert history.all()[0].candidate_build == "build-1"
