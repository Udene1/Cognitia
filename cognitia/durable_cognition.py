"""Durable projections for higher-level cognitive lifecycle state.

This module persists cognitive metadata, not executable Python callables. A
candidate's implementation remains an artifact that must be explicitly
rehydrated and verified before execution. Persistence therefore preserves
identity, provenance, lifecycle state, and build manifests without pretending
that serialization itself proves executable capability.
"""
from __future__ import annotations

from typing import Any

from .build import CognitiveBuild
from .candidate_registry import CandidateRecord
from .cognitive_history import EvaluationRecord
from .durable import DurableEvent, SQLiteCognitiveJournal
from .learning.scientific import Hypothesis, TestResult
from .self_model import CapabilityOutcome


class DurableCognitiveLedger:
    """Append-only durable projection of Cognitia's cognitive lifecycle."""

    def __init__(self, journal: SQLiteCognitiveJournal) -> None:
        self.journal = journal

    def record_candidate(self, record: CandidateRecord) -> DurableEvent:
        candidate = record.candidate
        event = DurableEvent(
            kind="candidate_state",
            source="candidate_registry",
            payload={
                "candidate_id": record.candidate_id,
                "state": record.state.value,
                "benchmark_score": record.benchmark_score,
                "verification_passed": record.verification_passed,
                "reason": record.reason,
                "candidate": {
                    "name": candidate.name,
                    "mode": candidate.mode.value,
                    "operations": list(candidate.operations),
                    "representation": candidate.representation,
                    "source_trace_ids": list(candidate.source_trace_ids),
                    "code_artifact": candidate.code_artifact,
                    "executable_rehydration_required": True,
                },
            },
        )
        return self.journal.append(event)

    def record_evaluation(self, record: EvaluationRecord) -> DurableEvent:
        event = DurableEvent(
            kind="evaluation",
            source="cognitive_history",
            payload={
                "candidate_id": record.candidate_id,
                "event": record.event.value,
                "build_id": record.build_id,
                "benchmark_name": record.benchmark_name,
                "baseline_score": record.baseline_score,
                "candidate_score": record.candidate_score,
                "regression": record.regression,
                "verification": record.verification.value if record.verification else None,
                "reason": record.reason,
            },
        )
        return self.journal.append(event)

    def record_build(self, build: CognitiveBuild) -> DurableEvent:
        event = DurableEvent(
            kind="cognitive_build",
            source="cognitive_build",
            payload={
                "build_id": build.build_id,
                "software_version": build.software_version,
                "parent_build": build.parent_build,
                "notes": build.notes,
                "capabilities": [
                    {
                        "name": capability.name,
                        "maturity": capability.maturity,
                        "status": capability.status,
                    }
                    for capability in build.capabilities
                ],
            },
        )
        return self.journal.append(event)

    def record_hypothesis(self, hypothesis: Hypothesis) -> DurableEvent:
        return self.journal.append(
            DurableEvent(
                kind="hypothesis_state",
                source="scientific_reasoning",
                payload={
                    "id": hypothesis.id,
                    "proposition": hypothesis.proposition,
                    "domain": hypothesis.domain,
                    "confidence": hypothesis.confidence,
                    "status": hypothesis.status,
                    "support_count": hypothesis.support_count,
                    "challenge_count": hypothesis.challenge_count,
                    "inconclusive_count": hypothesis.inconclusive_count,
                    "tested_conditions": list(hypothesis.tested_conditions),
                },
            )
        )

    def record_test_result(self, result: TestResult, *, hypothesis_id: str) -> DurableEvent:
        if not hypothesis_id.strip():
            raise ValueError("hypothesis_id is required")
        return self.journal.append(
            DurableEvent(
                kind="hypothesis_test",
                source="scientific_evaluator",
                payload={
                    "hypothesis_id": hypothesis_id,
                    "id": result.id,
                    "verdict": result.verdict,
                    "predicted": result.predicted,
                    "observed": result.observed,
                    "condition": result.condition,
                    "reliability": result.reliability,
                    "explanation": result.explanation,
                    "tested_at": result.tested_at.isoformat(),
                },
            )
        )

    def record_capability_outcome(self, outcome: CapabilityOutcome) -> DurableEvent:
        return self.journal.append(
            DurableEvent(
                kind="capability_outcome",
                source="self_model",
                payload={
                    "capability": outcome.capability,
                    "successful": outcome.successful,
                    "context": outcome.context,
                    "failure_mode": outcome.failure_mode,
                },
            )
        )

    def candidate_snapshots(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("candidate_state"))

    def evaluations(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("evaluation"))

    def builds(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("cognitive_build"))

    def hypotheses(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("hypothesis_state"))

    def hypothesis_tests(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("hypothesis_test"))

    def capability_outcomes(self) -> tuple[dict[str, Any], ...]:
        return tuple(event.payload for event in self.journal.by_kind("capability_outcome"))
