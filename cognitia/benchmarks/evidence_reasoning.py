"""Capability-level benchmark for solving evidence-poisoned problems.

This is deliberately above the evidence primitives: each case is a problem that
requires Cognitia to reason over provenance, contradiction, staleness, and the
need for another test. The benchmark never supplies the expected answer to the
solver; expectations are used only by the benchmark harness after solving.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from cognitia.evidence.convergence import EvidenceConvergenceEngine
from cognitia.evidence.model import Claim, EvidenceRecord, EvidenceSource, SourceLineage
from cognitia.evidence.model_checks import ModelConsistencyChecker, ModelConstraint


@dataclass(frozen=True)
class BenchmarkProblem:
    id: str
    question: str
    claim: Claim
    evidence: tuple[EvidenceRecord, ...]
    expected_status: str
    expected_independent_support: int
    expected_independent_contradiction: int
    expected_stale: tuple[str, ...] = ()
    model: ModelConstraint | None = None
    model_value: object | None = None
    expected_model_status: str | None = None


@dataclass(frozen=True)
class BenchmarkTrace:
    problem_id: str
    status: str
    independent_support_groups: int
    independent_contradiction_groups: int
    stale_evidence: tuple[str, ...]
    contradiction_detected: bool
    model_checked: bool
    model_status: str | None
    next_test: str | None
    naive_support_count: int
    naive_contradiction_count: int

    @property
    def capability_use_score(self) -> int:
        return sum((
            self.independent_support_groups > 0 or self.independent_contradiction_groups > 0,
            self.contradiction_detected,
            bool(self.stale_evidence),
            self.model_checked,
            self.next_test is not None,
        ))


@dataclass(frozen=True)
class BenchmarkResult:
    problem: BenchmarkProblem
    trace: BenchmarkTrace
    passed: bool


class EvidenceReasoningSolver:
    """A deterministic problem solver built from the evidence capabilities."""

    def __init__(self) -> None:
        self.convergence = EvidenceConvergenceEngine()
        self.models = ModelConsistencyChecker()

    def solve(self, problem: BenchmarkProblem) -> BenchmarkTrace:
        assessment = self.convergence.assess(problem.claim, problem.evidence)
        stale = self._stale(problem.evidence)
        model_status = None
        if problem.model is not None:
            result = self.models.check(problem.model, problem.model_value)  # type: ignore[arg-type]
            model_status = result.reason

        contradiction = assessment.independent_contradiction_groups > 0
        next_test = self._next_test(problem, assessment.status, contradiction, model_status)
        naive_support = sum(item.supports is True for item in problem.evidence)
        naive_contradiction = sum(item.supports is False for item in problem.evidence)
        return BenchmarkTrace(
            problem.id,
            assessment.status,
            assessment.independent_support_groups,
            assessment.independent_contradiction_groups,
            stale,
            contradiction,
            problem.model is not None,
            model_status,
            next_test,
            naive_support,
            naive_contradiction,
        )

    @staticmethod
    def _stale(evidence: tuple[EvidenceRecord, ...]) -> tuple[str, ...]:
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        stale: list[str] = []
        for item in evidence:
            if not item.measured_at:
                continue
            try:
                measured = datetime.fromisoformat(item.measured_at.replace("Z", "+00:00"))
            except ValueError:
                continue
            if measured < cutoff:
                stale.append(item.id)
        return tuple(stale)

    @staticmethod
    def _next_test(problem: BenchmarkProblem, status: str, contradiction: bool, model_status: str | None) -> str | None:
        if status in {"conflicted", "unresolved"}:
            return f"independent test for {problem.claim.id}"
        if contradiction or model_status == "model_conflict":
            return f"discriminating test for {problem.claim.id}"
        return None


class EvidenceReasoningBenchmark:
    def __init__(self, problems: tuple[BenchmarkProblem, ...] | None = None) -> None:
        self.problems = problems or benchmark_problems()
        self.solver = EvidenceReasoningSolver()

    def run(self) -> tuple[BenchmarkResult, ...]:
        results: list[BenchmarkResult] = []
        for problem in self.problems:
            trace = self.solver.solve(problem)
            passed = (
                trace.status == problem.expected_status
                and trace.independent_support_groups == problem.expected_independent_support
                and trace.independent_contradiction_groups == problem.expected_independent_contradiction
                and trace.stale_evidence == problem.expected_stale
                and (problem.expected_model_status is None or trace.model_status == problem.expected_model_status)
                and trace.capability_use_score >= 1
            )
            results.append(BenchmarkResult(problem, trace, passed))
        return tuple(results)


def _source(id: str, name: str, reliability: float, kind: str = "web") -> EvidenceSource:
    return EvidenceSource(id=id, name=name, kind=kind, reliability=reliability)


def _evidence(id: str, claim: Claim, source: EvidenceSource, supports: bool | None, content: str,
              upstream: tuple[str, ...] = (), measured_at: str | None = None) -> EvidenceRecord:
    return EvidenceRecord(
        id=id,
        claim_id=claim.id,
        source=source,
        content=content,
        supports=supports,
        lineage=SourceLineage(source.id, upstream) if upstream else None,
        measured_at=measured_at,
        method="benchmark-observation",
    )


def benchmark_problems() -> tuple[BenchmarkProblem, ...]:
    """Adversarial, deterministic problems; duplicated narratives share lineage."""
    p1 = Claim("power-a", "The device produces 100 units of output under the stated test conditions.", "measurement")
    original = _source("lab-original", "Independent lab", .95, "experiment")
    copies = tuple(
        _evidence(f"copy-{i}", p1, _source(f"copy-source-{i}", f"Copied article {i}", .55), True,
                   "The device produces 100 units.", upstream=("copy-origin",)) for i in range(6)
    )
    e1 = _evidence("primary-measurement", p1, original, False, "Controlled measurement produced 71 units.", measured_at="2026-06-10T00:00:00Z")
    p2 = Claim("release-safe", "Release 42 is safe to deploy.", "software")
    release = _source("release-test", "Independent release test", .95, "test")
    incident = _source("incident-db", "Production incident database", .95, "database")
    p3 = Claim("growth", "The system's current growth rate is 20 percent per month.", "economics")
    old = _source("old-report", "2023 market report", .9)
    recent = _source("recent-observation", "2026 customer observation", .9, "observation")
    p4 = Claim("free-fall", "An object falls with acceleration 9.81 m/s^2 in the stated idealized conditions.", "physics")
    physics = ModelConstraint(
        "gravity-model",
        "Newtonian near-surface gravity",
        "reported acceleration should be close to 9.81 m/s^2",
        lambda context: abs(float(context["value"]) - 9.81) < 0.05,
    )
    p5 = Claim("hidden-cause", "The service outage was caused by dependency X.", "incident")
    return (
        BenchmarkProblem("correlated-slop", "Does the device produce 100 units?", p1, copies + (e1,), "contradicted", 1, 1),
        BenchmarkProblem("independent-conflict", "Is release 42 safe?", p2, (
            _evidence("safe-test", p2, release, True, "Controlled test passed."),
            _evidence("incident", p2, incident, False, "Production failure occurred during the same release."),
        ), "conflicted", 1, 1),
        BenchmarkProblem("stale-data", "Is current growth 20 percent?", p3, (
            _evidence("old", p3, old, True, "Growth was 20 percent in 2023.", measured_at="2023-06-01T00:00:00Z"),
            _evidence("recent", p3, recent, False, "Current observed growth is 8 percent.", measured_at="2026-06-01T00:00:00Z"),
        ), "conflicted", 1, 1, ("old",)),
        BenchmarkProblem("model-check", "Is the reported acceleration consistent with the model?", p4, (
            _evidence("measurement", p4, _source("sensor", "Independent sensor", .9, "experiment"), True, "Measured acceleration: 8.2 m/s^2."),
        ), "supported", 1, 0, model=physics, model_value={"value": 8.2}, expected_model_status="model_conflict"),
        BenchmarkProblem("insufficient", "Was dependency X the cause?", p5, (
            _evidence("uncertain", p5, _source("logs", "Partial logs", .7, "database"), None, "Logs show a restart near the outage, but do not establish causality."),
        ), "unresolved", 0, 0),
    )


def format_results(results: tuple[BenchmarkResult, ...]) -> str:
    lines = ["EVIDENCE_REASONING_PROBLEM_SUCCESS"]
    for result in results:
        t = result.trace
        lines.append(f"PROBLEM: {result.problem.id} PASS={result.passed}")
        lines.append(f"  naive: {t.naive_support_count} support / {t.naive_contradiction_count} contradiction")
        lines.append(f"  independent: {t.independent_support_groups} support / {t.independent_contradiction_groups} contradiction")
        lines.append(f"  stale: {list(t.stale_evidence)}")
        lines.append(f"  contradiction_detected: {t.contradiction_detected}")
        lines.append(f"  model_checked: {t.model_checked} status={t.model_status}")
        lines.append(f"  next_test: {t.next_test}")
        lines.append(f"  conclusion: {t.status}")
    lines.append(f"PASSED: {sum(r.passed for r in results)}/{len(results)}")
    return "\n".join(lines)
