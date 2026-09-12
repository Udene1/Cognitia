"""Executable capability acquisition primitives.

This module moves capability acquisition beyond planning. Cognitia can compose
existing operations, learn reusable procedures from successful traces, or use a
controlled code constructor to create a candidate implementation. Nothing is
promoted merely because construction succeeded; candidates remain immutable
artifacts until tested and benchmarked.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping, Sequence


class AcquisitionMode(str, Enum):
    COMPOSE = "compose"
    LEARN_PROCEDURE = "learn_procedure"
    CONSTRUCT = "construct"


@dataclass(frozen=True)
class Operation:
    name: str
    run: Callable[[object], object]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("operation name cannot be empty")


@dataclass(frozen=True)
class CapabilityCandidate:
    name: str
    mode: AcquisitionMode
    operations: tuple[str, ...]
    implementation: Callable[[object], object]
    representation: str
    source_trace_ids: tuple[str, ...] = ()
    code_artifact: str | None = None

    def execute(self, value: object) -> object:
        return self.implementation(value)


@dataclass(frozen=True)
class ReasoningTrace:
    """A successful sequence that may be generalized into a procedure."""

    id: str
    operations: tuple[str, ...]
    input: object
    output: object
    context: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("trace id cannot be empty")
        if not self.operations:
            raise ValueError("trace must contain operations")


def compose_capability(
    name: str,
    operations: Sequence[Operation],
    *,
    representation: str,
) -> CapabilityCandidate:
    """Create a capability by composing already verified operations."""
    ops = tuple(operations)
    if not ops:
        raise ValueError("at least one operation is required")
    if not representation.strip():
        raise ValueError("representation cannot be empty")

    def run(value: object) -> object:
        current = value
        for operation in ops:
            current = operation.run(current)
        return current

    return CapabilityCandidate(
        name=name,
        mode=AcquisitionMode.COMPOSE,
        operations=tuple(operation.name for operation in ops),
        implementation=run,
        representation=representation,
    )


def learn_procedure(
    name: str,
    traces: Sequence[ReasoningTrace],
    operations: Mapping[str, Operation],
    *,
    representation: str,
) -> CapabilityCandidate:
    """Generalize a repeated successful operation sequence into a procedure."""
    if not traces:
        raise ValueError("at least one trace is required")
    sequence = traces[0].operations
    if not sequence or any(trace.operations != sequence for trace in traces):
        raise ValueError("traces must share the same operation sequence")
    if any(step not in operations for step in sequence):
        raise ValueError("trace references an unknown operation")

    def run(value: object) -> object:
        current = value
        for step in sequence:
            current = operations[step].run(current)
        return current

    return CapabilityCandidate(
        name=name,
        mode=AcquisitionMode.LEARN_PROCEDURE,
        operations=sequence,
        implementation=run,
        representation=representation,
        source_trace_ids=tuple(trace.id for trace in traces),
    )


def construct_capability(
    name: str,
    implementation: Callable[[object], object],
    *,
    operations: Sequence[str],
    representation: str,
    code_artifact: str,
) -> CapabilityCandidate:
    """Register a generated implementation as a candidate, not as live cognition."""
    if not operations:
        raise ValueError("constructed capability must declare its operations")
    if not representation.strip() or not code_artifact.strip():
        raise ValueError("representation and code artifact are required")
    return CapabilityCandidate(
        name=name,
        mode=AcquisitionMode.CONSTRUCT,
        operations=tuple(operations),
        implementation=implementation,
        representation=representation,
        code_artifact=code_artifact,
    )
