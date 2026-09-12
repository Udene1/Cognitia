"""Structured epistemic status for Cognitia's reasoning results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite


class EpistemicStatus(str, Enum):
    ESTABLISHED = "established"
    SUPPORTED = "supported"
    PREDICTION = "prediction"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    APPROXIMATION = "approximation"
    HEURISTIC = "heuristic"
    ANALOGY = "analogy"
    SPECULATION = "speculation"
    UNRESOLVED = "unresolved"
    CAPABILITY_LIMITED = "capability_limited"


@dataclass(frozen=True)
class VerificationPlan:
    """A concrete path for testing or strengthening a conclusion."""

    steps: tuple[str, ...]
    expected_value: float = 0.0

    def __post_init__(self) -> None:
        if not self.steps:
            raise ValueError("verification plan must contain at least one step")
        if any(not step.strip() for step in self.steps):
            raise ValueError("verification steps cannot be empty")
        if not isfinite(self.expected_value) or not 0.0 <= self.expected_value <= 1.0:
            raise ValueError("expected verification value must be between 0 and 1")


@dataclass(frozen=True)
class CapabilitySubstitution:
    """Records an explicit weaker-capability substitution."""

    required_capability: str
    available_capability: str
    purpose: str
    validity_limit: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.required_capability, "required capability"),
            (self.available_capability, "available capability"),
            (self.purpose, "purpose"),
            (self.validity_limit, "validity limit"),
        ):
            if not value.strip():
                raise ValueError(f"{label} cannot be empty")


@dataclass(frozen=True)
class ReasoningResult:
    """An answer together with the epistemic information needed to interpret it."""

    claim: str
    status: EpistemicStatus
    reasoning_method: str
    confidence: float
    assumptions: tuple[str, ...] = ()
    supporting_evidence: tuple[str, ...] = ()
    contradicting_evidence: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    substitution: CapabilitySubstitution | None = None
    verification: VerificationPlan | None = None

    def __post_init__(self) -> None:
        if not self.claim.strip():
            raise ValueError("claim cannot be empty")
        if not self.reasoning_method.strip():
            raise ValueError("reasoning method cannot be empty")
        if not isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be finite and between 0 and 1")
        if self.status is EpistemicStatus.CAPABILITY_LIMITED and not self.limitations:
            raise ValueError("capability-limited results must expose their limitations")
        if self.substitution is not None and self.status not in {
            EpistemicStatus.APPROXIMATION,
            EpistemicStatus.HYPOTHESIS,
            EpistemicStatus.INFERENCE,
            EpistemicStatus.CAPABILITY_LIMITED,
        }:
            raise ValueError("capability substitution requires a non-conclusive epistemic status")

    @property
    def requires_verification(self) -> bool:
        return self.verification is not None
