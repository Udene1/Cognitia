"""Cross-capability regression checks for cognitive build promotion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .benchmark import BenchmarkResult, BuildComparison, compare_builds


@dataclass(frozen=True)
class RegressionPolicy:
    """Promotion policy protecting existing capabilities."""

    max_regression: float = 0.0
    minimum_new_capability_improvement: float = 0.0

    def __post_init__(self) -> None:
        if self.max_regression < 0:
            raise ValueError("max_regression cannot be negative")
        if self.minimum_new_capability_improvement < 0:
            raise ValueError("minimum improvement cannot be negative")


@dataclass(frozen=True)
class RegressionFinding:
    capability: str
    comparison: BuildComparison
    regression: float
    protected: bool


@dataclass(frozen=True)
class PromotionDecision:
    eligible: bool
    primary: BuildComparison
    findings: tuple[RegressionFinding, ...]
    reason: str


def evaluate_promotion(
    baseline_primary: BenchmarkResult,
    candidate_primary: BenchmarkResult,
    protected_baseline: Iterable[BenchmarkResult],
    protected_candidate: Iterable[BenchmarkResult],
    policy: RegressionPolicy | None = None,
) -> PromotionDecision:
    """Determine whether a candidate improved without unacceptable regressions."""
    policy = policy or RegressionPolicy()
    primary = compare_builds(baseline_primary, candidate_primary)
    if primary.improvement < policy.minimum_new_capability_improvement:
        return PromotionDecision(
            False,
            primary,
            (),
            "new capability did not meet the minimum improvement threshold",
        )

    baseline = tuple(protected_baseline)
    candidate = tuple(protected_candidate)
    if len(baseline) != len(candidate):
        raise ValueError("protected benchmark sets must have equal length")

    findings: list[RegressionFinding] = []
    for old, new in zip(baseline, candidate):
        comparison = compare_builds(old, new)
        regression = max(0.0, -comparison.improvement)
        findings.append(
            RegressionFinding(
                capability=comparison.capability,
                comparison=comparison,
                regression=regression,
                protected=regression <= policy.max_regression,
            )
        )

    blocked = [f for f in findings if not f.protected]
    if blocked:
        return PromotionDecision(
            False,
            primary,
            tuple(findings),
            "candidate regresses a protected capability beyond policy tolerance",
        )

    return PromotionDecision(
        True,
        primary,
        tuple(findings),
        "candidate improved the target capability without unacceptable regressions",
    )
