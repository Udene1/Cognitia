"""Model-consistency checks for empirical claims.

Models constrain investigation; a failed check is evidence about the claim/model,
not an automatic declaration that either one is false.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping


@dataclass(frozen=True)
class ModelConstraint:
    id: str
    model: str
    description: str
    evaluator: Callable[[Mapping[str, object]], bool]

    def __post_init__(self) -> None:
        if not self.id or not self.model or not self.description:
            raise ValueError("model constraint identity and description are required")


@dataclass(frozen=True)
class ModelCheckResult:
    constraint_id: str
    model: str
    passed: bool | None
    reason: str


class ModelConsistencyChecker:
    def check(self, constraint: ModelConstraint, context: Mapping[str, object]) -> ModelCheckResult:
        try:
            passed = bool(constraint.evaluator(context))
        except Exception as exc:  # model applicability/measurement failure is evidence, not a crash
            return ModelCheckResult(constraint.id, constraint.model, None, f"check_unavailable:{type(exc).__name__}")
        return ModelCheckResult(constraint.id, constraint.model, passed, "consistent_with_model" if passed else "model_conflict")

    def check_all(self, constraints: tuple[ModelConstraint, ...], context: Mapping[str, object]) -> tuple[ModelCheckResult, ...]:
        return tuple(self.check(item, context) for item in constraints)
