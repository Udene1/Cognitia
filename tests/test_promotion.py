from cognitia.benchmark import BenchmarkCase, BenchmarkResult, BenchmarkSuite
from cognitia.build import CapabilityRecord, create_build
from cognitia.capability_acquisition import AcquisitionMode, CapabilityCandidate
from cognitia.candidate_registry import CandidateRecord, CandidateRegistry
from cognitia.promotion import CognitivePromotionOrchestrator
from cognitia.verification import VerificationPlan, VerificationStep


def _result(benchmark: str, capability: str, build: str, score: float) -> BenchmarkResult:
    suite = BenchmarkSuite(benchmark, capability, (BenchmarkCase("case", 1, 1.0),))
    return BenchmarkResult(benchmark, capability, build, (), score)


def _candidate() -> CapabilityCandidate:
    return CapabilityCandidate(
        name="new_reasoner",
        mode=AcquisitionMode.COMPOSE,
        operations=("op",),
        implementation=lambda value: value,
        representation="identity transformation",
    )


def _plan() -> VerificationPlan:
    return VerificationPlan(
        candidate_id="candidate-1",
        steps=(VerificationStep("s1", "candidate executes safely"),),
    )


def test_successful_gated_promotion_creates_child_build():
    registry = CandidateRegistry((CandidateRecord("candidate-1", _candidate()),))
    registry.benchmark("candidate-1", 1.0)
    parent = create_build("build-1", "0.1", (CapabilityRecord("base", "mature"),))

    result = CognitivePromotionOrchestrator(registry).evaluate(
        "candidate-1",
        verification_plan=_plan(),
        verifier=lambda step: True,
        baseline_primary=_result("primary", "new_reasoner", "build-1", 0.5),
        candidate_primary=_result("primary", "new_reasoner", "candidate", 0.9),
        parent_build=parent,
        build_id="build-2",
        software_version="0.2",
    )

    assert result.decision is not None and result.decision.eligible
    assert result.build is not None
    assert result.build.parent_build == "build-1"
    assert result.build.has_capability("new_reasoner")
    assert registry.get("candidate-1").state.value == "promoted"


def test_regression_holds_candidate_without_mutating_parent_build():
    registry = CandidateRegistry((CandidateRecord("candidate-1", _candidate()),))
    registry.benchmark("candidate-1", 1.0)
    parent = create_build("build-1", "0.1", (CapabilityRecord("base", "mature"),))

    result = CognitivePromotionOrchestrator(registry).evaluate(
        "candidate-1",
        verification_plan=_plan(),
        verifier=lambda step: True,
        baseline_primary=_result("primary", "new_reasoner", "build-1", 0.5),
        candidate_primary=_result("primary", "new_reasoner", "candidate", 0.9),
        protected_baseline=(_result("protected", "base", "build-1", 1.0),),
        protected_candidate=(_result("protected", "base", "candidate", 0.7),),
        parent_build=parent,
        build_id="build-2",
        software_version="0.2",
    )

    assert result.decision is not None and not result.decision.eligible
    assert result.build is None
    assert result.decision.disposition.value == "hold_for_balancing"
    assert parent.build_id == "build-1"
    assert registry.get("candidate-1").state.value == "held"
