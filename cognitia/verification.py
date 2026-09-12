"""Verification machinery for capability candidates and cognitive conclusions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence


class VerificationOutcome(str, Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class VerificationStep:
    id: str
    description: str
    expected: object
    cost: float = 1.0

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.description.strip():
            raise ValueError("verification step requires id and description")
        if self.cost <= 0:
            raise ValueError("verification cost must be positive")


@dataclass(frozen=True)
class VerificationPlan:
    claim: str
    steps: tuple[VerificationStep, ...]
    expected_value: float

    def __post_init__(self) -> None:
        if not self.claim.strip() or not self.steps:
            raise ValueError("claim and at least one verification step are required")
        if not 0.0 <= self.expected_value <= 1.0:
            raise ValueError("expected value must be between 0 and 1")


@dataclass(frozen=True)
class VerificationResult:
    plan: str
    outcome: VerificationOutcome
    evidence: tuple[str, ...] = ()
    changed_confidence: float | None = None


Verifier = Callable[[VerificationStep], VerificationOutcome]


def execute_plan(plan: VerificationPlan, verifier: Verifier) -> VerificationResult:
    outcomes = [verifier(step) for step in plan.steps]
    if all(o is VerificationOutcome.VERIFIED for o in outcomes):
        outcome = VerificationOutcome.VERIFIED
    elif any(o is VerificationOutcome.FAILED for o in outcomes):
        outcome = VerificationOutcome.FAILED
    else:
        outcome = VerificationOutcome.INCONCLUSIVE
    return VerificationResult(plan.claim, outcome)
