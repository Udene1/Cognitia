from cognitia.benchmark import BenchmarkCase, BenchmarkOutcome, BenchmarkSuite, CaseResult
from cognitia.regression import CandidateDisposition, RegressionPolicy, evaluate_promotion


def result(suite: BenchmarkSuite, build: str, outcome: BenchmarkOutcome):
    return suite.evaluate(build, lambda case: CaseResult(case.id, outcome))


def test_regression_holds_candidate_instead_of_discarding_it() -> None:
    target = BenchmarkSuite("causal", "causal_reasoning", (BenchmarkCase("a", 1, 1),))
    protected = BenchmarkSuite("math", "deterministic_reasoning", (BenchmarkCase("a", 1, 1),))

    decision = evaluate_promotion(
        result(target, "C0.1", BenchmarkOutcome.FAIL),
        result(target, "C0.2", BenchmarkOutcome.PASS),
        (result(protected, "C0.1", BenchmarkOutcome.PASS),),
        (result(protected, "C0.2", BenchmarkOutcome.FAIL),),
    )

    assert not decision.eligible
    assert decision.disposition is CandidateDisposition.HOLD_FOR_BALANCING
    assert decision.retain_candidate
    assert decision.primary.candidate_build == "C0.2"


def test_candidate_can_be_accepted_when_balanced() -> None:
    target = BenchmarkSuite("causal", "causal_reasoning", (BenchmarkCase("a", 1, 1),))
    protected = BenchmarkSuite("math", "deterministic_reasoning", (BenchmarkCase("a", 1, 1),))

    decision = evaluate_promotion(
        result(target, "C0.1", BenchmarkOutcome.FAIL),
        result(target, "C0.2", BenchmarkOutcome.PASS),
        (result(protected, "C0.1", BenchmarkOutcome.PASS),),
        (result(protected, "C0.2", BenchmarkOutcome.PASS),),
    )

    assert decision.eligible
    assert decision.disposition is CandidateDisposition.ACCEPT
    assert decision.retain_candidate


def test_missing_improvement_also_holds_candidate_for_further_work() -> None:
    target = BenchmarkSuite("target", "new_capability", (BenchmarkCase("a", 1, 1),))

    decision = evaluate_promotion(
        result(target, "C0.1", BenchmarkOutcome.PASS),
        result(target, "C0.2", BenchmarkOutcome.PASS),
        (),
        (),
        RegressionPolicy(minimum_new_capability_improvement=0.1),
    )

    assert not decision.eligible
    assert decision.disposition is CandidateDisposition.HOLD_FOR_BALANCING
    assert decision.retain_candidate
