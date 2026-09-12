"""Evaluate acquired capabilities without mutating the active cognitive build."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .benchmark import BenchmarkResult, BenchmarkSuite, CaseResult, BenchmarkOutcome
from .build import CognitiveBuild
from .capability_acquisition import CapabilityCandidate
from .regression import PromotionDecision, RegressionPolicy, evaluate_promotion


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate: CapabilityCandidate
    primary: BenchmarkResult
    promotion: PromotionDecision | None


def benchmark_candidate(
    candidate: CapabilityCandidate,
    suite: BenchmarkSuite,
    *,
    build_id: str,
) -> BenchmarkResult:
    """Run a candidate against a deterministic benchmark without activation."""
    if suite.capability != candidate.name:
        raise ValueError("benchmark capability must match candidate name")

    def evaluate(case) -> CaseResult:
        try:
            actual = candidate.execute(case.input)
        except Exception as exc:  # candidate failure is benchmark evidence, not activation
            return CaseResult(case.id, BenchmarkOutcome.FAIL, explanation=f"execution failed: {exc!r}")
        outcome = BenchmarkOutcome.PASS if actual == case.expected else BenchmarkOutcome.FAIL
        return CaseResult(case.id, outcome, actual=actual)

    return suite.evaluate(build_id, evaluate)


def evaluate_candidate(
    candidate: CapabilityCandidate,
    primary_suite: BenchmarkSuite,
    *,
    candidate_build: CognitiveBuild,
    baseline_primary: BenchmarkResult,
    protected_baseline: Iterable[BenchmarkResult] = (),
    protected_candidate: Iterable[BenchmarkResult] = (),
    policy: RegressionPolicy | None = None,
) -> CandidateEvaluation:
    """Benchmark first, then optionally decide whether promotion is safe."""
    primary = benchmark_candidate(candidate, primary_suite, build_id=candidate_build.build_id)
    promotion = evaluate_promotion(
        baseline_primary,
        primary,
        protected_baseline,
        protected_candidate,
        policy,
    )
    return CandidateEvaluation(candidate, primary, promotion)
