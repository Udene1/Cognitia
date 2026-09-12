"""Failure-driven discovery of missing cognitive machinery."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .capabilities import CapabilityAvailability, CapabilityGap
from .capability_acquisition import (
    AcquisitionMode,
    CapabilityCandidate,
    Operation,
    ReasoningTrace,
    compose_capability,
    learn_procedure,
)


class DiscoveryConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class FailureObservation:
    problem_type: str
    required_capability: str
    missing_operation: str
    context: str
    reason: str


@dataclass(frozen=True)
class CapabilityPattern:
    operation_sequence: tuple[str, ...]
    supporting_trace_ids: tuple[str, ...]
    contexts: tuple[str, ...]
    confidence: DiscoveryConfidence


@dataclass(frozen=True)
class AcquisitionDecision:
    capability: str
    mode: AcquisitionMode
    reason: str
    confidence: DiscoveryConfidence
    operation_sequence: tuple[str, ...]


class CapabilityDiscoveryEngine:
    """Turn repeated failures and successful traces into acquisition decisions."""

    def discover_pattern(self, traces: Sequence[ReasoningTrace], *, minimum_repetitions: int = 2) -> CapabilityPattern | None:
        if minimum_repetitions < 2:
            raise ValueError("minimum_repetitions must be at least 2")
        groups: dict[tuple[str, ...], list[ReasoningTrace]] = {}
        for trace in traces:
            groups.setdefault(trace.operations, []).append(trace)
        candidates = [group for group in groups.values() if len(group) >= minimum_repetitions]
        if not candidates:
            return None
        best = max(candidates, key=len)
        confidence = DiscoveryConfidence.HIGH if len(best) >= 4 else DiscoveryConfidence.MEDIUM
        return CapabilityPattern(best[0].operations, tuple(t.id for t in best), tuple(t.context for t in best if t.context), confidence)

    def decide(
        self,
        gap: CapabilityGap,
        *,
        available_operations: Mapping[str, Operation],
        successful_traces: Sequence[ReasoningTrace] = (),
        construction_available: bool = False,
    ) -> AcquisitionDecision:
        if gap.availability is CapabilityAvailability.AVAILABLE:
            raise ValueError("acquisition is only meaningful for incomplete capabilities")
        pattern = self.discover_pattern(successful_traces)
        if pattern is not None and all(step in available_operations for step in pattern.operation_sequence):
            return AcquisitionDecision(gap.required, AcquisitionMode.LEARN_PROCEDURE, "repeated successful traces expose a reusable operation sequence", pattern.confidence, pattern.operation_sequence)
        if available_operations:
            sequence = tuple(available_operations)
            return AcquisitionDecision(gap.required, AcquisitionMode.COMPOSE, "existing verified operations can be composed before constructing new machinery", DiscoveryConfidence.MEDIUM, sequence)
        if construction_available:
            return AcquisitionDecision(gap.required, AcquisitionMode.CONSTRUCT, "no reusable operation is available; controlled construction is required", DiscoveryConfidence.LOW, ())
        raise ValueError("no acquisition path is currently available")

    def acquire_candidate(
        self,
        decision: AcquisitionDecision,
        *,
        available_operations: Mapping[str, Operation],
        successful_traces: Sequence[ReasoningTrace] = (),
        implementation=None,
        representation: str,
        code_artifact: str | None = None,
    ) -> CapabilityCandidate:
        if decision.mode is AcquisitionMode.LEARN_PROCEDURE:
            return learn_procedure(decision.capability, successful_traces, available_operations, representation=representation)
        if decision.mode is AcquisitionMode.COMPOSE:
            return compose_capability(decision.capability, [available_operations[n] for n in decision.operation_sequence], representation=representation)
        if implementation is None or not code_artifact:
            raise ValueError("construction requires an implementation and code artifact")
        from .capability_acquisition import construct_capability
        return construct_capability(decision.capability, implementation, operations=decision.operation_sequence or ("constructed_operation",), representation=representation, code_artifact=code_artifact)
