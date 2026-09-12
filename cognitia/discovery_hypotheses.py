"""Bounded hypothesis-space construction from explanatory gaps.

This module does not generate prose or claim novelty. It transforms an explicit
model description into alternative structures that can be tested. The
transformations are intentionally inspectable so later research can replace
them with learned search without changing the epistemic contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Iterable

from .discovery import ExplanatoryGap, HypothesisCandidate


class HypothesisTransform(StrEnum):
    RELAX_ASSUMPTION = "relax_assumption"
    REVERSE_ASSUMPTION = "reverse_assumption"
    PARTITION_CONTEXT = "partition_context"
    ADD_MISSING_VARIABLE = "add_missing_variable"


@dataclass(frozen=True)
class ExplanatoryModel:
    """A minimal explicit model from which alternatives can be constructed."""

    id: str
    proposition: str
    assumptions: tuple[str, ...] = ()
    variables: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.proposition.strip():
            raise ValueError("model id and proposition are required")


@dataclass(frozen=True)
class HypothesisAlternative:
    """A generated alternative plus the structural transformation that made it."""

    id: str
    proposition: str
    transform: HypothesisTransform
    source_model: str
    changed_element: str
    epistemic_status: str = "hypothesis"
    novelty_status: str = "unassessed"

    def as_candidate(self, gap: ExplanatoryGap) -> HypothesisCandidate:
        return HypothesisCandidate(
            id=self.id,
            proposition=self.proposition,
            derived_from_gap=gap.observation_ids,
            novelty_status=self.novelty_status,
            epistemic_status=self.epistemic_status,
        )


class HypothesisSpaceBuilder:
    """Construct a bounded, traceable alternative hypothesis space."""

    def build(
        self,
        model: ExplanatoryModel,
        gap: ExplanatoryGap,
        *,
        missing_variables: Iterable[str] = (),
        transforms: Iterable[HypothesisTransform] | None = None,
    ) -> tuple[HypothesisAlternative, ...]:
        selected = tuple(transforms) if transforms is not None else tuple(HypothesisTransform)
        out: list[HypothesisAlternative] = []

        for transform in selected:
            if transform is HypothesisTransform.RELAX_ASSUMPTION:
                for assumption in model.assumptions:
                    out.append(self._alternative(
                        model, transform, assumption,
                        f"{model.proposition}; assume '{assumption}' may not hold",
                    ))
            elif transform is HypothesisTransform.REVERSE_ASSUMPTION:
                for assumption in model.assumptions:
                    out.append(self._alternative(
                        model, transform, assumption,
                        f"{model.proposition}; '{assumption}' may operate in the opposite direction",
                    ))
            elif transform is HypothesisTransform.PARTITION_CONTEXT:
                for variable in model.variables:
                    out.append(self._alternative(
                        model, transform, variable,
                        f"{model.proposition}; effect may differ across '{variable}' contexts",
                    ))
            elif transform is HypothesisTransform.ADD_MISSING_VARIABLE:
                for variable in missing_variables:
                    if variable.strip():
                        out.append(self._alternative(
                            model, transform, variable,
                            f"{model.proposition}; '{variable}' may explain the gap",
                        ))

        return tuple(self._dedupe(out))

    @staticmethod
    def _alternative(
        model: ExplanatoryModel,
        transform: HypothesisTransform,
        changed: str,
        proposition: str,
    ) -> HypothesisAlternative:
        digest = sha256(f"{model.id}|{transform}|{changed}|{proposition}".encode()).hexdigest()[:16]
        return HypothesisAlternative(
            id=f"h-{digest}",
            proposition=proposition,
            transform=transform,
            source_model=model.id,
            changed_element=changed,
        )

    @staticmethod
    def _dedupe(items: Iterable[HypothesisAlternative]) -> list[HypothesisAlternative]:
        seen: set[str] = set()
        result: list[HypothesisAlternative] = []
        for item in items:
            if item.id not in seen:
                seen.add(item.id)
                result.append(item)
        return result
