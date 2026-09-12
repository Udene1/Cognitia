"""Append-only history of cognitive evaluation and promotion evidence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .benchmark import BenchmarkResult
from .regression import PromotionDecision
from .verification import VerificationResult


@dataclass(frozen=True)
class EvaluationRecord:
    """One complete candidate evaluation snapshot."""
    candidate_id: str
    candidate_build: str
    primary: BenchmarkResult
    protected: tuple[BenchmarkResult, ...]
    verification: VerificationResult | None = None
    promotion: PromotionDecision | None = None
    disposition: str = "evaluated"
    reason: str = ""


class BenchmarkHistory:
    """Retain every evaluation; later records never erase earlier evidence."""
    def __init__(self, records: Iterable[EvaluationRecord] = ()) -> None:
        self._records = list(records)

    def record(self, evaluation: EvaluationRecord) -> None:
        if not evaluation.candidate_id.strip():
            raise ValueError("candidate_id is required")
        self._records.append(evaluation)

    def all(self) -> tuple[EvaluationRecord, ...]:
        return tuple(self._records)

    def for_candidate(self, candidate_id: str) -> tuple[EvaluationRecord, ...]:
        return tuple(record for record in self._records if record.candidate_id == candidate_id)

    def latest(self, candidate_id: str) -> EvaluationRecord | None:
        records = self.for_candidate(candidate_id)
        return records[-1] if records else None
