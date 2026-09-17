"""Auditable provenance for communication capabilities.

This module records *how* a communication capability entered Cognitia.  It is
research metadata, not a communication policy: recording a capability here
must never be treated as evidence that Cognitia learned it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterable


class CapabilityOrigin(StrEnum):
    """How a capability was introduced into the system."""

    DEVELOPER_SPECIFIED = "developer_specified"
    EXPERIENCE_DERIVED = "experience_derived"
    TRANSFER_DERIVED = "transfer_derived"
    OBSERVED = "observed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CapabilityProvenance:
    """Evidence lineage for one capability claim.

    ``origin`` describes provenance, while ``status`` describes the current
    research interpretation.  These are deliberately separate so that a
    capability can be executable without being mislabelled as learned.
    """

    capability: str
    origin: CapabilityOrigin
    introduced_by: str
    evidence: tuple[str, ...] = ()
    validated_by: tuple[str, ...] = ()
    later_boundaries: tuple[str, ...] = ()
    current_status: str = "unresolved"
    independent_of_handholding: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.capability.strip():
            raise ValueError("capability must not be empty")
        if not self.introduced_by.strip():
            raise ValueError("introduced_by must not be empty")
        if not self.current_status.strip():
            raise ValueError("current_status must not be empty")

    @property
    def learned_claim_supported(self) -> bool:
        """Whether the record explicitly supports an experience-derived claim."""

        return (
            self.origin == CapabilityOrigin.EXPERIENCE_DERIVED
            and self.independent_of_handholding
            and bool(self.validated_by)
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "capability": self.capability,
            "origin": self.origin.value,
            "introduced_by": self.introduced_by,
            "evidence": list(self.evidence),
            "validated_by": list(self.validated_by),
            "later_boundaries": list(self.later_boundaries),
            "current_status": self.current_status,
            "independent_of_handholding": self.independent_of_handholding,
            "learned_claim_supported": self.learned_claim_supported,
            "notes": self.notes,
        }


@dataclass
class CommunicationProvenanceRegistry:
    """Small deterministic registry used to audit research provenance."""

    records: list[CapabilityProvenance] = field(default_factory=list)

    def add(self, record: CapabilityProvenance) -> None:
        if any(existing.capability == record.capability for existing in self.records):
            raise ValueError(f"duplicate capability provenance: {record.capability}")
        self.records.append(record)

    def get(self, capability: str) -> CapabilityProvenance:
        for record in self.records:
            if record.capability == capability:
                return record
        raise KeyError(capability)

    def as_dicts(self) -> list[dict[str, object]]:
        return [record.as_dict() for record in self.records]

    @classmethod
    def from_iterable(cls, records: Iterable[CapabilityProvenance]) -> "CommunicationProvenanceRegistry":
        registry = cls()
        for record in records:
            registry.add(record)
        return registry
