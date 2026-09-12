"""Compare independently written programs by normalized computation, not syntax."""
from __future__ import annotations

from dataclasses import dataclass

from .code_representation import ComputationalRepresentation, PythonCodeInterpreter


@dataclass(frozen=True)
class StructuralMatch:
    """Result of comparing two source-derived computational representations."""

    equivalent_family: bool
    shared_operations: tuple[str, ...]
    shared_control_flow: tuple[str, ...]
    confidence: float
    epistemic_status: str = "inference"


class CodeStructureComparator:
    """Find invariant computational structure across independently written code."""

    def __init__(self, interpreter: PythonCodeInterpreter | None = None) -> None:
        self._interpreter = interpreter or PythonCodeInterpreter()

    def compare(self, left_source: str, right_source: str) -> StructuralMatch:
        left = self._interpreter.interpret(left_source)
        right = self._interpreter.interpret(right_source)
        return self.compare_representations(left, right)

    @staticmethod
    def compare_representations(
        left: ComputationalRepresentation,
        right: ComputationalRepresentation,
    ) -> StructuralMatch:
        shared_operations = tuple(sorted(set(left.operations) & set(right.operations)))
        shared_control = tuple(sorted(set(left.control_flow) & set(right.control_flow)))
        same_family = left.algorithm_family == right.algorithm_family and left.algorithm_family != "unknown"
        operation_ratio = len(shared_operations) / max(len(set(left.operations) | set(right.operations)), 1)
        control_ratio = len(shared_control) / max(len(set(left.control_flow) | set(right.control_flow)), 1)
        confidence = min(left.confidence, right.confidence) * (
            0.6 * float(same_family) + 0.25 * operation_ratio + 0.15 * control_ratio
        )
        return StructuralMatch(
            equivalent_family=same_family,
            shared_operations=shared_operations,
            shared_control_flow=shared_control,
            confidence=round(confidence, 6),
        )
