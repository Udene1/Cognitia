"""Cognitia's model of its own cognitive capabilities.

This module does not perform reasoning itself. It gives the reasoning system an
explicit representation of what machinery is available, how reliable it is,
and where capability gaps exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Iterable


class CapabilityAvailability(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    MISSING = "missing"


@dataclass(frozen=True)
class Capability:
    """A cognitive capability known by the self-model."""

    name: str
    domain: str
    reliability: float = 0.5
    maturity: str = "experimental"
    limitations: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("capability name cannot be empty")
        if not self.domain.strip():
            raise ValueError("capability domain cannot be empty")
        if not isfinite(self.reliability) or not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be finite and between 0 and 1")
        if not self.maturity.strip():
            raise ValueError("maturity cannot be empty")


@dataclass(frozen=True)
class CapabilityGap:
    """A mismatch between what a problem requires and what Cognitia has."""

    required: str
    availability: CapabilityAvailability
    available_capability: str | None = None
    substitution_allowed: bool = True
    substitution_note: str | None = None

    def __post_init__(self) -> None:
        if not self.required.strip():
            raise ValueError("required capability cannot be empty")
        if self.availability is CapabilityAvailability.AVAILABLE and self.available_capability is None:
            raise ValueError("available capability is required when availability is AVAILABLE")
        if self.substitution_allowed and self.availability is CapabilityAvailability.AVAILABLE:
            raise ValueError("substitution is only meaningful for partial or missing capabilities")
        if self.substitution_allowed and not self.substitution_note:
            raise ValueError("substitution note is required when substitution is allowed")


@dataclass(frozen=True)
class CapabilityAssessment:
    """Assessment of one required capability for a particular problem."""

    required: str
    availability: CapabilityAvailability
    capability: Capability | None = None
    gap: CapabilityGap | None = None

    def __post_init__(self) -> None:
        if not self.required.strip():
            raise ValueError("required capability cannot be empty")
        if self.availability is CapabilityAvailability.AVAILABLE and self.capability is None:
            raise ValueError("an available capability must be supplied")
        if self.availability is not CapabilityAvailability.AVAILABLE and self.gap is None:
            raise ValueError("a capability gap must be supplied when capability is incomplete")


@dataclass
class SelfModel:
    """Evidence-backed inventory of Cognitia's current cognitive machinery."""

    capabilities: dict[str, Capability] = field(default_factory=dict)

    def register(self, capability: Capability) -> None:
        """Register or replace a capability by name."""
        self.capabilities[capability.name] = capability

    def get(self, name: str) -> Capability | None:
        return self.capabilities.get(name)

    def assess(self, required: str) -> CapabilityAssessment:
        """Assess whether a required capability is available."""
        capability = self.get(required)
        if capability is None:
            gap = CapabilityGap(
                required=required,
                availability=CapabilityAvailability.MISSING,
                substitution_allowed=False,
            )
            return CapabilityAssessment(
                required=required,
                availability=CapabilityAvailability.MISSING,
                gap=gap,
            )

        return CapabilityAssessment(
            required=required,
            availability=CapabilityAvailability.AVAILABLE,
            capability=capability,
        )

    def assess_many(self, required: Iterable[str]) -> tuple[CapabilityAssessment, ...]:
        return tuple(self.assess(name) for name in required)

    def can_attempt(self, required: str) -> bool:
        """Return whether the self-model contains any registered machinery for a direct attempt."""
        return self.get(required) is not None

    def capabilities_for_domain(self, domain: str) -> tuple[Capability, ...]:
        return tuple(
            capability
            for capability in self.capabilities.values()
            if capability.domain == domain
        )
