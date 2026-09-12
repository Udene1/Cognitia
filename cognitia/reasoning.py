"""Small reasoning boundary for qualified cognitive attempts."""

from __future__ import annotations

from dataclasses import dataclass

from .epistemic import (
    CapabilitySubstitution,
    EpistemicStatus,
    ReasoningResult,
    VerificationPlan,
)
from .routing import ReasoningRoute


@dataclass(frozen=True)
class QualifiedAttempt:
    """The result of attempting a problem with the currently available route."""

    result: ReasoningResult


def qualify_attempt(
    *,
    claim: str,
    route: ReasoningRoute,
    confidence: float,
    assumptions: tuple[str, ...] = (),
    supporting_evidence: tuple[str, ...] = (),
    contradicting_evidence: tuple[str, ...] = (),
    verification: VerificationPlan | None = None,
) -> QualifiedAttempt:
    """Convert a cognitive route into an explicitly qualified result.

    This function deliberately does not judge whether the claim is true. It
    records what Cognitia's current machinery can justify and prevents a
    fallback mechanism from being represented as an established result.
    """
    if route.substitution_required:
        status = EpistemicStatus.CAPABILITY_LIMITED
        substitution = CapabilitySubstitution(
            required_capability=route.required_capability,
            available_capability=route.capability.name if route.capability else route.method,
            purpose="produce the strongest useful hypothesis or approximation available",
            validity_limit=route.limitation or "the fallback cannot establish the required capability",
        )
        limitations = (route.limitation or "A weaker capability was substituted.",)
    elif route.availability.value == "available":
        status = EpistemicStatus.INFERENCE
        substitution = None
        limitations = ()
    else:
        status = EpistemicStatus.UNRESOLVED
        substitution = None
        limitations = (route.limitation or "Required capability is unavailable.",)

    return QualifiedAttempt(
        ReasoningResult(
            claim=claim,
            status=status,
            reasoning_method=route.method,
            confidence=confidence,
            assumptions=assumptions,
            supporting_evidence=supporting_evidence,
            contradicting_evidence=contradicting_evidence,
            limitations=limitations,
            substitution=substitution,
            verification=verification,
        )
    )
