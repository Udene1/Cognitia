"""Auditable history for candidate evaluation and cognitive-build promotion.

The active candidate state is intentionally not the historical record. A
cognitive system needs to remember failed promotions, regressions, holds, and
verification outcomes so future balancing can learn from them instead of
restarting from the latest state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .benchmark import BuildComparison
from .verification import VerificationOutcome


class PromotionEvent(str, Enum):
    BENCHMARKED = "benchmarked"
    VERIFIED = "verified"
    HELD = "held"
    PROMOTED = "promoted"


@dataclass(frozen=True)
class EvaluationRecord:
    candidate_id: str
    event: PromotionEvent
    build_id: str | None = None
    benchmark_name: str | None = None
    baseline_score: float | None = None
    candidate_score: float | None = None
    regression: float = 0.0
    verification: VerificationOutcome | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id is required")
        if self.baseline_score is not None and not 0.0 <= self.baseline_score <= 1.0:
            raise ValueError("baseline score must be between 0 and 1")
        if self.candidate_score is not None and not 0.0 <= self.candidate_score <= 1.0:
            raise ValueError("candidate score must be between 0 and 1")
        if self.regression < 0.0:
            raise ValueError("regression cannot be negative")


class CognitiveHistory:
    """Append-only in-memory history; persistence can be layered on later."""

    def __init__(self, records: Iterable[EvaluationRecord] = ()) -> None:
        self._records = list(records)

    def record(self, entry: EvaluationRecord) -> EvaluationRecord:
        self._records.append(entry)
        return entry

    def all(self) -> tuple[EvaluationRecord, ...]:
        return tuple(self._records)

    def for_candidate(self, candidate_id: str) -> tuple[EvaluationRecord, ...]:
        return tuple(r for r in self._records if r.candidate_id == candidate_id)

    def regressions(self, candidate_id: str | None = None) -> tuple[EvaluationRecord, ...]:
        records = self._records if candidate_id is None else self.for_candidate(candidate_id)
        return tuple(r for r in records if r.regression > 0.0)

    def latest(self, candidate_id: str) -> EvaluationRecord | None:
        for record in reversed(self._records):
            if record.candidate_id == candidate_id:
                return record
        return None


def evaluation_from_comparison(
    candidate_id: str,
    comparison: BuildComparison,
    *,
    event: PromotionEvent = PromotionEvent.BENCHMARKED,
    reason: str = "",
) -> EvaluationRecord:
    """Convert a benchmark comparison into an auditable history entry."""
    return EvaluationRecord(
        candidate_id=candidate_id,
        event=event,
        benchmark_name=comparison.benchmark,
        baseline_score=comparison.baseline_score,
        candidate_score=comparison.candidate_score,
        regression=max(0.0, -comparison.improvement),
        reason=reason,
    )
