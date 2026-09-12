"""Orchestrate candidate verification, benchmarking, regression, and builds."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .benchmark import BenchmarkResult, compare_builds
from .build import CapabilityRecord, CognitiveBuild, create_build
from .candidate_registry import CandidateRegistry, CandidateState
from .cognitive_history import CognitiveHistory, EvaluationRecord, PromotionEvent, evaluation_from_comparison
from .regression import PromotionDecision, RegressionPolicy, evaluate_promotion
from .verification import VerificationPlan, VerificationResult, execute_plan


@dataclass(frozen=True)
class PromotionEvaluation:
    candidate_id: str
    verification: VerificationResult
    decision: PromotionDecision | None
    build: CognitiveBuild | None
    history: tuple[EvaluationRecord, ...] = ()


class CognitivePromotionOrchestrator:
    """Move a candidate through gates without mutating the live build.

    Every evaluation is also written to append-only cognitive history. A hold
    therefore becomes evidence for future balancing rather than a dead end.
    """

    def __init__(self, registry: CandidateRegistry, history: CognitiveHistory | None = None) -> None:
        self.registry = registry
        self.history = history or CognitiveHistory()

    def evaluate(
        self,
        candidate_id: str,
        *,
        verification_plan: VerificationPlan,
        verifier: Callable[[object], bool],
        baseline_primary: BenchmarkResult,
        candidate_primary: BenchmarkResult,
        protected_baseline: Iterable[BenchmarkResult] = (),
        protected_candidate: Iterable[BenchmarkResult] = (),
        policy: RegressionPolicy | None = None,
        parent_build: CognitiveBuild,
        build_id: str,
        software_version: str,
    ) -> PromotionEvaluation:
        record = self.registry.get(candidate_id)
        if record is None:
            raise KeyError(candidate_id)
        if record.state not in {CandidateState.BENCHMARKED, CandidateState.HELD}:
            raise ValueError("candidate must be benchmarked or held before promotion evaluation")

        comparison = compare_builds(baseline_primary, candidate_primary)
        self.history.record(evaluation_from_comparison(candidate_id, comparison))

        verification = execute_plan(verification_plan, verifier)
        if verification.outcome.value != "verified":
            held = self.registry.hold(candidate_id, "verification did not establish the candidate")
            self.history.record(
                EvaluationRecord(
                    candidate_id=candidate_id,
                    event=PromotionEvent.HELD,
                    verification=verification.outcome,
                    reason=held.reason,
                )
            )
            return PromotionEvaluation(held.candidate_id, verification, None, None, self.history.for_candidate(candidate_id))

        self.registry.verify(candidate_id)
        self.history.record(
            EvaluationRecord(
                candidate_id=candidate_id,
                event=PromotionEvent.VERIFIED,
                verification=verification.outcome,
            )
        )
        decision = evaluate_promotion(
            baseline_primary,
            candidate_primary,
            protected_baseline,
            protected_candidate,
            policy,
        )
        if not decision.eligible:
            held = self.registry.hold(candidate_id, decision.reason)
            self.history.record(
                EvaluationRecord(
                    candidate_id=candidate_id,
                    event=PromotionEvent.HELD,
                    verification=verification.outcome,
                    regression=max((finding.regression for finding in decision.findings), default=0.0),
                    reason=decision.reason,
                )
            )
            return PromotionEvaluation(held.candidate_id, verification, decision, None, self.history.for_candidate(candidate_id))

        promoted = self.registry.promote(candidate_id)
        capabilities = list(parent_build.capabilities)
        names = {cap.name for cap in capabilities}
        if promoted.candidate.name not in names:
            capabilities.append(
                CapabilityRecord(
                    name=promoted.candidate.name,
                    maturity="benchmarked-and-verified",
                    status="active",
                )
            )
        else:
            capabilities = [
                CapabilityRecord(cap.name, cap.maturity, "active" if cap.name == promoted.candidate.name else cap.status)
                for cap in capabilities
            ]
        build = create_build(
            build_id,
            software_version,
            capabilities,
            parent_build=parent_build.build_id,
            notes=f"Promoted candidate {candidate_id} after verification, benchmark, and regression evaluation.",
        )
        self.history.record(
            EvaluationRecord(
                candidate_id=candidate_id,
                event=PromotionEvent.PROMOTED,
                build_id=build.build_id,
                verification=verification.outcome,
            )
        )
        return PromotionEvaluation(promoted.candidate_id, verification, decision, build, self.history.for_candidate(candidate_id))
