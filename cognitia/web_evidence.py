"""Evaluation of acquired web observations before they enter cognition."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from datetime import datetime, timezone
from typing import Iterable

from .environment import EnvironmentObservation


@dataclass(frozen=True)
class EvidenceAssessment:
    observation: EnvironmentObservation
    fingerprint: str
    accepted: bool
    reason: str
    effective_at: datetime | None = None
    expires_at: datetime | None = None


class WebEvidenceEvaluator:
    """Deduplicate and gate source observations without deciding their truth."""

    def __init__(self, *, minimum_reliability: float = 0.0) -> None:
        if not 0.0 <= minimum_reliability <= 1.0:
            raise ValueError("minimum_reliability must be between 0 and 1")
        self.minimum_reliability = minimum_reliability

    @staticmethod
    def fingerprint(observation: EnvironmentObservation) -> str:
        payload = f"{observation.source}|{observation.content.strip()}".encode()
        return sha256(payload).hexdigest()[:24]

    def assess(
        self,
        observations: Iterable[EnvironmentObservation],
        *,
        now: datetime | None = None,
    ) -> tuple[EvidenceAssessment, ...]:
        now = now or datetime.now(timezone.utc)
        seen: set[str] = set()
        result: list[EvidenceAssessment] = []
        for observation in observations:
            fingerprint = self.fingerprint(observation)
            metadata = dict(observation.metadata)
            effective = self._time(metadata.get("effective_at"))
            expires = self._time(metadata.get("expires_at"))
            if fingerprint in seen:
                result.append(EvidenceAssessment(observation, fingerprint, False, "duplicate", effective, expires))
                continue
            seen.add(fingerprint)
            if observation.reliability < self.minimum_reliability:
                result.append(EvidenceAssessment(observation, fingerprint, False, "below_reliability_threshold", effective, expires))
                continue
            if effective and effective > now:
                result.append(EvidenceAssessment(observation, fingerprint, False, "not_yet_effective", effective, expires))
                continue
            if expires and expires <= now:
                result.append(EvidenceAssessment(observation, fingerprint, False, "expired", effective, expires))
                continue
            result.append(EvidenceAssessment(observation, fingerprint, True, "accepted_as_evidence", effective, expires))
        return tuple(result)

    @staticmethod
    def _time(value: object) -> datetime | None:
        if value is None:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
