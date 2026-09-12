"""Scientific testing primitives for challenging Cognitia's own models.

These primitives deliberately separate observation from belief revision. A failed
prediction is evidence against a model under a tested condition, not permission
to immediately discard a well-supported theory or declare a new causal law.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Hypothesis:
    """A falsifiable proposition with an explicit empirical history."""

    proposition: str
    domain: str
    confidence: float = 0.5
    id: str = field(default_factory=lambda: str(uuid4()))
    support_count: int = 0
    challenge_count: int = 0
    inconclusive_count: int = 0
    tested_conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if min(self.support_count, self.challenge_count, self.inconclusive_count) < 0:
            raise ValueError("test counts cannot be negative")

    @property
    def status(self) -> str:
        """Return an evidence status without pretending it is absolute truth."""
        if self.challenge_count and not self.support_count:
            return "challenged"
        if self.support_count and not self.challenge_count:
            return "supported"
        if self.support_count and self.challenge_count:
            return "mixed"
        return "untested"

    def with_test(self, result: "TestResult") -> "Hypothesis":
        """Record a test while preserving the caller's confidence model.

        Confidence is intentionally not changed automatically. Statistical or
        domain-specific belief revision must be supplied by a later evaluator
        that knows the relevant error model and likelihoods.
        """
        counts = {
            "supporting": self.support_count,
            "challenging": self.challenge_count,
            "inconclusive": self.inconclusive_count,
        }
        counts[result.verdict] += 1
        condition = result.condition
        conditions = self.tested_conditions
        if condition and condition not in conditions:
            conditions = conditions + (condition,)
        return replace(
            self,
            support_count=counts["supporting"],
            challenge_count=counts["challenging"],
            inconclusive_count=counts["inconclusive"],
            tested_conditions=conditions,
        )


@dataclass(frozen=True)
class TestResult:
    """Outcome of comparing a model prediction with an observation."""

    verdict: str
    predicted: Any
    observed: Any
    condition: str = ""
    reliability: float = 1.0
    explanation: str = ""
    tested_at: datetime = field(default_factory=utc_now)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.verdict not in {"supporting", "challenging", "inconclusive"}:
            raise ValueError("verdict must be supporting, challenging, or inconclusive")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be between 0 and 1")


class ScientificEvaluator:
    """Compare predictions with observations without changing beliefs."""

    def evaluate(
        self,
        *,
        predicted: Any,
        observed: Any,
        condition: str = "",
        reliability: float = 1.0,
        explanation: str = "",
    ) -> TestResult:
        """Create a test result from an explicit prediction comparison.

        Equality is intentionally strict here. Numeric tolerances, uncertainty
        intervals, measurement error, and statistical significance belong in
        domain-specific evaluators rather than being silently invented here.
        """
        verdict = "supporting" if predicted == observed else "challenging"
        return TestResult(
            verdict=verdict,
            predicted=predicted,
            observed=observed,
            condition=condition,
            reliability=reliability,
            explanation=explanation,
        )
