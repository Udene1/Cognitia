from cognitia.benchmark import BenchmarkCase, BenchmarkOutcome, BenchmarkSuite, CaseResult, BenchmarkResult
from cognitia.cognitive_history import CognitiveHistory, EvaluationRecord, PromotionEvent, evaluation_from_comparison


def _result(name: str, score: float) -> BenchmarkResult:
    suite = BenchmarkSuite(
        name=name,
        capability="reasoning",
        cases=(BenchmarkCase("case", "input", "expected"),),
    )
    return BenchmarkResult(
        benchmark=name,
        capability="reasoning",
        build="build",
        cases=(CaseResult("case", BenchmarkOutcome.PASS, "actual", "ok"),),
        score=score,
    )


def test_history_retains_multiple_evaluations_and_regressions():
    history = CognitiveHistory()
    comparison = __import__("cognitia.benchmark", fromlist=["compare_builds"]).compare_builds(
        _result("reasoning", 1.0), _result("reasoning", 0.8)
    )
    history.record(evaluation_from_comparison("candidate", comparison))
    history.record(EvaluationRecord("candidate", PromotionEvent.HELD, reason="regression"))

    assert len(history.for_candidate("candidate")) == 2
    assert len(history.regressions("candidate")) == 1
    assert history.latest("candidate").event is PromotionEvent.HELD
