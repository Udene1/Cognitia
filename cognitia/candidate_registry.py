"""Lifecycle registry for capabilities Cognitia discovers but has not promoted."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .capability_acquisition import CapabilityCandidate


class CandidateState(str, Enum):
    DISCOVERED = "discovered"
    BENCHMARKED = "benchmarked"
    VERIFIED = "verified"
    HELD = "held"
    PROMOTED = "promoted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class CandidateRecord:
    candidate_id: str
    candidate: CapabilityCandidate
    state: CandidateState = CandidateState.DISCOVERED
    benchmark_score: float | None = None
    verification_passed: bool = False
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id is required")
        if self.benchmark_score is not None and not 0.0 <= self.benchmark_score <= 1.0:
            raise ValueError("benchmark score must be between 0 and 1")
        if self.state is CandidateState.VERIFIED and not self.verification_passed:
            raise ValueError("verified candidates must have passed verification")
        if self.state is CandidateState.PROMOTED and not self.verification_passed:
            raise ValueError("promoted candidates must have passed verification")


class CandidateRegistry:
    """Append-style logical registry; state transitions replace records, never delete them."""

    def __init__(self, records: Iterable[CandidateRecord] = ()) -> None:
        self._records = {record.candidate_id: record for record in records}

    def add(self, record: CandidateRecord) -> None:
        if record.candidate_id in self._records:
            raise ValueError("candidate already exists")
        self._records[record.candidate_id] = record

    def get(self, candidate_id: str) -> CandidateRecord | None:
        return self._records.get(candidate_id)

    def all(self) -> tuple[CandidateRecord, ...]:
        return tuple(self._records.values())

    def benchmark(self, candidate_id: str, score: float) -> CandidateRecord:
        record = self._require(candidate_id)
        updated = replace(record, state=CandidateState.BENCHMARKED, benchmark_score=score)
        self._records[candidate_id] = updated
        return updated

    def verify(self, candidate_id: str) -> CandidateRecord:
        record = self._require(candidate_id)
        if record.state not in {CandidateState.BENCHMARKED, CandidateState.VERIFIED, CandidateState.HELD}:
            raise ValueError("candidate must be benchmarked before verification")
        updated = replace(record, state=CandidateState.VERIFIED, verification_passed=True)
        self._records[candidate_id] = updated
        return updated

    def hold(self, candidate_id: str, reason: str) -> CandidateRecord:
        record = self._require(candidate_id)
        if not reason.strip():
            raise ValueError("hold reason is required")
        updated = replace(record, state=CandidateState.HELD, reason=reason)
        self._records[candidate_id] = updated
        return updated

    def promote(self, candidate_id: str) -> CandidateRecord:
        record = self._require(candidate_id)
        if record.state is not CandidateState.VERIFIED:
            raise ValueError("only verified candidates can be promoted")
        updated = replace(record, state=CandidateState.PROMOTED)
        self._records[candidate_id] = updated
        return updated

    def _require(self, candidate_id: str) -> CandidateRecord:
        record = self.get(candidate_id)
        if record is None:
            raise KeyError(candidate_id)
        return record
