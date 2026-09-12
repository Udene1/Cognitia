from cognitia.balancing import BalancingEngine, BalancingStrategy
from cognitia.benchmark import BenchmarkResult, BuildComparison, CaseResult, BenchmarkOutcome
from cognitia.regression import RegressionFinding


def comparison(capability: str, improvement: float) -> BuildComparison:
    return BuildComparison(
        benchmark="protected",
        capability=capability,
        baseline_build="base",
        candidate_build="candidate",
        baseline_score=0.9,
        candidate_score=0.9 + improvement,
    )


def test_regression_produces_multiple_repair_hypotheses() -> None:
    finding = RegressionFinding("retrieval", comparison("retrieval", -0.2), 0.2, False)

    proposals = BalancingEngine().propose((finding,))

    assert {proposal.strategy for proposal in proposals} == {
        BalancingStrategy.SELECTIVE_COMPOSITION,
        BalancingStrategy.METHOD_PRIORITY,
        BalancingStrategy.CAPABILITY_BOUNDARY,
        BalancingStrategy.CONTEXT_ROUTING,
    }
    assert all("retrieval" == proposal.target_capability for proposal in proposals)


def test_non_regression_produces_no_repair_proposal() -> None:
    finding = RegressionFinding("retrieval", comparison("retrieval", 0.0), 0.0, True)

    assert BalancingEngine().propose((finding,)) == ()
