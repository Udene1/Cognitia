"""Controlled acquisition of missing cognitive capabilities.

Capability acquisition is deliberately a proposal system, not arbitrary
self-modification. Cognitia may diagnose a gap and design an acquisition plan,
but deployment remains an explicit later step after validation and approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class AcquisitionStage(str, Enum):
    PROPOSED = "proposed"
    SPECIFIED = "specified"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    BENCHMARKED = "benchmarked"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class CapabilityRequirement:
    """A capability gap that has been demonstrated by a task or failure."""

    name: str
    domain: str
    reason: str
    evidence: tuple[str, ...] = ()
    required_inputs: tuple[str, ...] = ()
    expected_outputs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, label in ((self.name, "name"), (self.domain, "domain"), (self.reason, "reason")):
            if not value.strip():
                raise ValueError(f"{label} cannot be empty")


@dataclass(frozen=True)
class AcquisitionProposal:
    """A bounded plan for constructing or learning one missing capability."""

    requirement: CapabilityRequirement
    representation: str
    acquisition_steps: tuple[str, ...]
    tests: tuple[str, ...]
    benchmarks: tuple[str, ...]
    safety_constraints: tuple[str, ...]
    stage: AcquisitionStage = AcquisitionStage.PROPOSED

    def __post_init__(self) -> None:
        if not self.representation.strip():
            raise ValueError("representation cannot be empty")
        if not self.acquisition_steps:
            raise ValueError("at least one acquisition step is required")
        if not self.tests:
            raise ValueError("at least one test is required")
        if not self.benchmarks:
            raise ValueError("at least one benchmark is required")
        if not self.safety_constraints:
            raise ValueError("safety constraints are required")

    def advance(self, stage: AcquisitionStage) -> "AcquisitionProposal":
        """Return a new proposal state; never mutate an existing plan."""
        return AcquisitionProposal(
            requirement=self.requirement,
            representation=self.representation,
            acquisition_steps=self.acquisition_steps,
            tests=self.tests,
            benchmarks=self.benchmarks,
            safety_constraints=self.safety_constraints,
            stage=stage,
        )


def propose_capability_acquisition(
    requirement: CapabilityRequirement,
    *,
    representation: str,
    acquisition_steps: Iterable[str],
    tests: Iterable[str],
    benchmarks: Iterable[str],
    safety_constraints: Iterable[str],
) -> AcquisitionProposal:
    """Create a validated acquisition proposal without deploying anything."""
    return AcquisitionProposal(
        requirement=requirement,
        representation=representation,
        acquisition_steps=tuple(acquisition_steps),
        tests=tuple(tests),
        benchmarks=tuple(benchmarks),
        safety_constraints=tuple(safety_constraints),
    )
