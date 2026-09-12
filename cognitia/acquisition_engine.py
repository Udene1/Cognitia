"""Goal-directed capability discovery and candidate construction.

The engine turns an observed capability gap into a concrete acquisition decision.
It does not deploy code. It searches the capabilities Cognitia already has,
looks for repeated successful procedures, and only falls back to construction
when composition/generalization cannot satisfy the gap.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .capability_acquisition import (
    AcquisitionMode,
    CapabilityCandidate,
    Operation,
    ReasoningTrace,
    compose_capability,
    construct_capability,
    learn_procedure,
)


@dataclass(frozen=True)
class CapabilityGapSignal:
    """A concrete observation that a required capability is missing or weak."""

    required_capability: str
    candidate_name: str
    representation: str
    operation_sequence: tuple[str, ...] = ()
    traces: tuple[ReasoningTrace, ...] = ()
    allow_construction: bool = False

    def __post_init__(self) -> None:
        if not self.required_capability.strip() or not self.candidate_name.strip():
            raise ValueError("capability names are required")
        if not self.representation.strip():
            raise ValueError("representation is required")


@dataclass(frozen=True)
class AcquisitionDecision:
    """Why the engine chose an acquisition mode."""

    mode: AcquisitionMode
    reason: str
    confidence: float
    source_trace_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("acquisition reason is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("decision confidence must be between 0 and 1")


@dataclass(frozen=True)
class AcquisitionPlan:
    signal: CapabilityGapSignal
    decision: AcquisitionDecision
    candidate: CapabilityCandidate


CodeConstructor = Callable[[CapabilityGapSignal], tuple[Callable[[object], object], str]]


class CapabilityAcquisitionEngine:
    """Discover the least-complex viable path to a missing capability."""

    def __init__(self, operations: Mapping[str, Operation], *, min_repetitions: int = 2) -> None:
        if min_repetitions < 2:
            raise ValueError("min_repetitions must be at least 2")
        self._operations = dict(operations)
        self._min_repetitions = min_repetitions

    def plan(self, signal: CapabilityGapSignal, *, constructor: CodeConstructor | None = None) -> AcquisitionPlan:
        sequence = signal.operation_sequence or self._repeated_sequence(signal.traces)
        traces = tuple(signal.traces)

        if sequence and all(step in self._operations for step in sequence):
            if len(traces) >= self._min_repetitions and all(trace.operations == sequence for trace in traces):
                candidate = learn_procedure(
                    signal.candidate_name,
                    traces,
                    self._operations,
                    representation=signal.representation,
                )
                return AcquisitionPlan(
                    signal,
                    AcquisitionDecision(
                        AcquisitionMode.LEARN_PROCEDURE,
                        "The same successful operation sequence repeated enough times to justify a reusable procedure.",
                        min(1.0, 0.5 + 0.1 * len(traces)),
                        tuple(trace.id for trace in traces),
                    ),
                    candidate,
                )

            candidate = compose_capability(
                signal.candidate_name,
                [self._operations[step] for step in sequence],
                representation=signal.representation,
            )
            return AcquisitionPlan(
                signal,
                AcquisitionDecision(
                    AcquisitionMode.COMPOSE,
                    "Existing verified operations can solve the gap without inventing a new primitive.",
                    0.85,
                ),
                candidate,
            )

        if signal.allow_construction and constructor is not None:
            implementation, artifact = constructor(signal)
            candidate = construct_capability(
                signal.candidate_name,
                implementation,
                operations=signal.operation_sequence or (signal.required_capability,),
                representation=signal.representation,
                code_artifact=artifact,
            )
            return AcquisitionPlan(
                signal,
                AcquisitionDecision(
                    AcquisitionMode.CONSTRUCT,
                    "Composition and repeated-procedure learning could not satisfy the gap; controlled construction was explicitly allowed.",
                    0.55,
                ),
                candidate,
            )

        raise ValueError("no viable acquisition path: composition is unavailable and construction is not authorized")

    def _repeated_sequence(self, traces: Sequence[ReasoningTrace]) -> tuple[str, ...]:
        if not traces:
            return ()
        counts: dict[tuple[str, ...], int] = {}
        for trace in traces:
            counts[trace.operations] = counts.get(trace.operations, 0) + 1
        repeated = [(count, sequence) for sequence, count in counts.items() if count >= self._min_repetitions]
        if not repeated:
            return ()
        repeated.sort(key=lambda item: (-item[0], item[1]))
        return repeated[0][1]
