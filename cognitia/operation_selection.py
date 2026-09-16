"""Evaluate available operations against the current cognitive state.

This module is deliberately an experimental bridge. It does not claim that
Cognitia understands requests or learns a routing policy. It makes one thing
observable: given several permitted operations, what state-derived reasons
cause one operation to be preferred over another, and what evidence would be
needed to revise that choice?
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .experience import CognitiveState
from .information_need import InformationNeed, InformationNeedKind
from .state_action_generation import AvailableOperation


@dataclass(frozen=True)
class OperationOption:
    operation: AvailableOperation
    cost: float = 1.0
    risk: float = 0.0

    def __post_init__(self) -> None:
        if self.cost < 0 or self.risk < 0:
            raise ValueError("cost and risk must be non-negative")


@dataclass(frozen=True)
class OperationAssessment:
    operation: AvailableOperation
    expected_state_improvement: float
    cost: float
    risk: float
    net_value: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class OperationChoice:
    selected: OperationAssessment | None
    assessments: tuple[OperationAssessment, ...]


class OperationSelector:
    """Rank permitted operations using an explicit, inspectable hypothesis."""

    def assess(
        self,
        state: CognitiveState,
        need: InformationNeed,
        options: Sequence[OperationOption],
    ) -> OperationChoice:
        assessments: list[OperationAssessment] = []
        for option in options:
            capability = option.operation.capability.lower()
            reasons: list[str] = []
            improvement = 0.10

            if need.kind is InformationNeedKind.EXTERNAL_EVIDENCE and "external" in capability:
                improvement += 0.80
                reasons.append("current information need explicitly requires external evidence")
            elif need.kind is InformationNeedKind.COMPUTATION and "comput" in capability:
                improvement += 0.80
                reasons.append("current information need is computational")
            elif need.kind is InformationNeedKind.LOCAL_EVIDENCE and "inspect" in capability:
                improvement += 0.55
                reasons.append("current state points toward local evidence")
            elif need.kind is InformationNeedKind.NONE and "reason" in capability:
                improvement += 0.55
                reasons.append("state already contains evidence, so reasoning can exploit it without acquisition")
            elif need.kind is InformationNeedKind.UNRESOLVED:
                if state.evidence_ids and "compare" in capability:
                    improvement += 0.45
                    reasons.append("unresolved state contains evidence that can be compared")
                elif "inspect" in capability:
                    improvement += 0.30
                    reasons.append("inspection may reduce unresolved uncertainty")

            if not reasons:
                reasons.append("no state-derived special advantage identified")

            net_value = improvement - option.cost - option.risk
            assessments.append(
                OperationAssessment(
                    operation=option.operation,
                    expected_state_improvement=improvement,
                    cost=option.cost,
                    risk=option.risk,
                    net_value=net_value,
                    reasons=tuple(reasons),
                )
            )

        ranked = tuple(sorted(assessments, key=lambda item: (-item.net_value, item.operation.name)))
        return OperationChoice(selected=ranked[0] if ranked else None, assessments=ranked)
