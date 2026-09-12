from cognitia.balancing import BalancingEngine, BalancingStrategy
from cognitia.benchmark import BuildComparison
from cognitia.capability_acquisition import CapabilityCandidate, AcquisitionMode
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


def capability(name: str, fn) -> CapabilityCandidate:
    return CapabilityCandidate(
        name=name,
        mode=AcquisitionMode.CONSTRUCT,
        operations=(name,),
        implementation=fn,
        representation=name,
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


def test_repair_candidate_routes_between_baseline_and_candidate() -> None:
    finding = RegressionFinding("retrieval", comparison("retrieval", -0.2), 0.2, False)
    proposal = BalancingEngine().propose((finding,))[0]
    baseline = capability("retrieval", lambda value: f"baseline:{value}")
    candidate = capability("retrieval", lambda value: f"candidate:{value}")

    repaired = BalancingEngine().repair(
        proposal,
        candidate,
        baseline,
        selector=lambda value: value == "safe",
    )

    assert repaired.execute("safe") == "candidate:safe"
    assert repaired.execute("unsafe") == "baseline:unsafe"
    assert repaired.mode is AcquisitionMode.COMPOSE
    assert proposal.strategy.value in repaired.representation


def test_repair_requires_matching_capability_names() -> None:
    finding = RegressionFinding("retrieval", comparison("retrieval", -0.2), 0.2, False)
    proposal = BalancingEngine().propose((finding,))[0]
    baseline = capability("retrieval", lambda value: value)
    candidate = capability("planning", lambda value: value)

    try:
        BalancingEngine().repair(proposal, candidate, baseline, selector=lambda _: True)
    except ValueError as exc:
        assert "candidate capability" in str(exc)
    else:
        raise AssertionError("repair should reject mismatched capability names")
