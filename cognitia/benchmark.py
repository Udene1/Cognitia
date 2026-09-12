"""Benchmark cognitive capabilities and compare cognitive builds.

Benchmarks are deliberately separate from capability implementation. A capability
can claim to work; a benchmark provides repeatable evidence about whether it
actually performs better on a defined task.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Callable, Iterable, Sequence


class BenchmarkOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class BenchmarkCase:
    """One reproducible task used to evaluate a capability."""

    id: str
    input: object
    expected: object
    context: str = ""
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("benchmark case id cannot be empty")
        if not isfinite(self.weight) or self.weight <= 0:
            raise ValueError("benchmark case weight must be finite and positive")


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    outcome: BenchmarkOutcome
    actual: object = None
    explanation: str = ""


@dataclass(frozen=True)
class BenchmarkResult:
    """Immutable result of evaluating one capability on one benchmark suite."""

    benchmark: str
    capability: str
    build: str
    cases: tuple[CaseResult, ...]
    score: float

    def __post_init__(self) -> None:
        if not self.benchmark.strip() or not self.capability.strip() or not self.build.strip():
            raise ValueError("benchmark, capability, and build are required")
        if not isfinite(self.score) or not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be finite and between 0 and 1")


@dataclass(frozen=True)
class BuildComparison:
    """Comparison of two cognitive builds on the same benchmark."""

    benchmark: str
    capability: str
    baseline_build: str
    candidate_build: str
    baseline_score: float
    candidate_score: float

    @property
    def improvement(self) -> float:
        return self.candidate_score - self.baseline_score

    @property
    def improved(self) -> bool:
        return self.improvement > 0.0


Evaluator = Callable[[BenchmarkCase], CaseResult]


@dataclass
class BenchmarkSuite:
    """A deterministic suite of cases with a pluggable evaluator."""

    name: str
    capability: str
    cases: tuple[BenchmarkCase, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.capability.strip():
            raise ValueError("benchmark name and capability are required")
        if not self.cases:
            raise ValueError("benchmark suite must contain at least one case")
        ids = [case.id for case in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("benchmark case ids must be unique")

    def evaluate(self, build: str, evaluator: Evaluator) -> BenchmarkResult:
        if not build.strip():
            raise ValueError("build is required")
        results = tuple(evaluator(case) for case in self.cases)
        if len(results) != len(self.cases):
            raise ValueError("evaluator must return exactly one result per case")
        by_id = {result.case_id: result for result in results}
        if set(by_id) != {case.id for case in self.cases}:
            raise ValueError("evaluator returned unknown or missing case ids")
        total_weight = sum(case.weight for case in self.cases)
        earned = sum(
            case.weight
            for case in self.cases
            if by_id[case.id].outcome is BenchmarkOutcome.PASS
        )
        return BenchmarkResult(
            benchmark=self.name,
            capability=self.capability,
            build=build,
            cases=results,
            score=earned / total_weight,
        )


def compare_builds(
    baseline: BenchmarkResult,
    candidate: BenchmarkResult,
) -> BuildComparison:
    """Compare two results only when they represent the same benchmark."""
    if baseline.benchmark != candidate.benchmark:
        raise ValueError("builds must be evaluated on the same benchmark")
    if baseline.capability != candidate.capability:
        raise ValueError("builds must evaluate the same capability")
    return BuildComparison(
        benchmark=baseline.benchmark,
        capability=baseline.capability,
        baseline_build=baseline.build,
        candidate_build=candidate.build,
        baseline_score=baseline.score,
        candidate_score=candidate.score,
    )
