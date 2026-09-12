"""Evidence-aware revision of scientific hypothesis test history.

Revision records what changed and why. It does not turn one failed prediction
into automatic falsification or invent confidence updates without a defined
revision policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .scientific import Hypothesis, TestResult


class RevisionAction(str, Enum):
    RETAIN = "retain"
    DOWNGRADE = "downgrade"
    CHALLENGE = "challenge"
    SUSPEND = "suspend"
    REVISE = "revise"


@dataclass(frozen=True)
class RevisionDecision:
    action: RevisionAction
    reason: str
    revised_confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("revision reason is required")
        if self.revised_confidence is not None and not 0.0 <= self.revised_confidence <= 1.0:
            raise ValueError("revised confidence must be between 0 and 1")


def revise_hypothesis(
    hypothesis: Hypothesis,
    result: TestResult,
    *,
    decision: RevisionDecision,
) -> Hypothesis:
    """Apply an explicit revision decision while retaining test history.

    The caller must choose the revision policy. This keeps empirical evidence
    separate from the judgment used to change confidence.
    """
    updated = hypothesis.with_test(result)
    if decision.revised_confidence is None:
        return updated
    from dataclasses import replace
    return replace(updated, confidence=decision.revised_confidence)
