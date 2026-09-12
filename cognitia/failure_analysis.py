"""Failure analysis and capability-gap diagnosis.

Failures are evidence about *what kind* of machinery is missing.  The
analyzer deliberately avoids collapsing every failure into a generic domain
gap: a missing fact, a bad representation, an invalid assumption, and an
algorithmic limitation require different acquisition strategies.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence


class FailureClass(str, Enum):
    MISSING_KNOWLEDGE = "missing_knowledge"
    MISSING_REPRESENTATION = "missing_representation"
    MISSING_PRIMITIVE = "missing_primitive"
    MISSING_ALGORITHM = "missing_algorithm"
    INVALID_ASSUMPTION = "invalid_assumption"
    INSUFFICIENT_PRECISION = "insufficient_precision"
    CONTEXT_MISMATCH = "context_mismatch"
    CAPABILITY_CONFLICT = "capability_conflict"
    INSUFFICIENT_SEARCH = "insufficient_search"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FailureObservation:
    """Structured evidence produced by an unsuccessful attempt."""

    attempt_id: str
    task: str
    description: str
    failure_class: FailureClass
    required_capability: str | None = None
    context: str = ""
    observed_output: str = ""
    expected_output: str = ""
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.attempt_id.strip() or not self.task.strip():
            raise ValueError("attempt_id and task are required")
        if not self.description.strip():
            raise ValueError("failure description is required")


@dataclass(frozen=True)
class CapabilityGapDiagnosis:
    """Smallest actionable capability gap inferred from a failure."""

    capability: str
    failure_class: FailureClass
    confidence: float
    rationale: str
    prerequisites: tuple[str, ...] = ()
    related_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.capability.strip() or not self.rationale.strip():
            raise ValueError("capability and rationale are required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class FailureAnalyzer:
    """Turn failure evidence into a qualified, minimal capability diagnosis."""

    def diagnose(
        self,
        failure: FailureObservation,
        *,
        available_capabilities: Sequence[str] = (),
        capability_relations: Mapping[str, Sequence[str]] | None = None,
    ) -> CapabilityGapDiagnosis:
        available = set(available_capabilities)
        if failure.required_capability and failure.required_capability not in available:
            return CapabilityGapDiagnosis(
                failure.required_capability,
                failure.failure_class,
                0.9,
                "The attempt explicitly identified a required capability that is not currently available.",
            )

        names = {
            FailureClass.MISSING_KNOWLEDGE: "knowledge_acquisition",
            FailureClass.MISSING_REPRESENTATION: "representation_construction",
            FailureClass.MISSING_PRIMITIVE: "primitive_operation_construction",
            FailureClass.MISSING_ALGORITHM: "algorithm_construction",
            FailureClass.INVALID_ASSUMPTION: "assumption_analysis",
            FailureClass.INSUFFICIENT_PRECISION: "precision_control",
            FailureClass.CONTEXT_MISMATCH: "context_modeling",
            FailureClass.CAPABILITY_CONFLICT: "capability_balancing",
            FailureClass.INSUFFICIENT_SEARCH: "search_strategy",
            FailureClass.UNKNOWN: "failure_diagnosis",
        }
        capability = names[failure.failure_class]
        related = tuple(capability_relations.get(capability, ())) if capability_relations else ()
        return CapabilityGapDiagnosis(
            capability,
            failure.failure_class,
            0.65 if failure.failure_class is not FailureClass.UNKNOWN else 0.35,
            f"Failure classified as {failure.failure_class.value}; the diagnosis targets the smallest reusable machinery implied by that class rather than the whole task domain.",
            related_capabilities=related,
        )
