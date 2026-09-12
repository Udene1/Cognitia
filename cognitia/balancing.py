"""Generate explicit repair strategies for capability regressions.

A regression is not a deletion command. This module turns the evidence from a
blocked promotion into bounded repair proposals that can be benchmarked again.
It deliberately proposes strategies rather than silently changing cognition.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .regression import RegressionFinding


class BalancingStrategy(str, Enum):
    SELECTIVE_COMPOSITION = "selective_composition"
    METHOD_PRIORITY = "method_priority"
    CAPABILITY_BOUNDARY = "capability_boundary"
    CONTEXT_ROUTING = "context_routing"


@dataclass(frozen=True)
class BalancingProposal:
    """A candidate repair hypothesis derived from observed regression."""

    capability: str
    strategy: BalancingStrategy
    target_capability: str
    rationale: str
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.capability.strip() or not self.target_capability.strip():
            raise ValueError("capability names are required")
        if not self.rationale.strip():
            raise ValueError("rationale is required")


class BalancingEngine:
    """Produce deterministic, evidence-linked repair hypotheses."""

    def propose(self, findings: Iterable[RegressionFinding]) -> tuple[BalancingProposal, ...]:
        proposals: list[BalancingProposal] = []
        for finding in findings:
            if finding.regression <= 0.0:
                continue
            target = finding.comparison.capability
            proposals.extend(
                (
                    BalancingProposal(
                        capability=target,
                        strategy=BalancingStrategy.SELECTIVE_COMPOSITION,
                        target_capability=target,
                        rationale="Restrict the new capability to the composition path that provides its measured improvement instead of replacing unrelated behavior.",
                        constraints=("preserve protected capability benchmark",),
                    ),
                    BalancingProposal(
                        capability=target,
                        strategy=BalancingStrategy.METHOD_PRIORITY,
                        target_capability=target,
                        rationale="Treat the existing method as the preferred path where it is empirically stronger, while retaining the candidate method as an alternative.",
                        constraints=("route only when candidate evidence is sufficient",),
                    ),
                    BalancingProposal(
                        capability=target,
                        strategy=BalancingStrategy.CAPABILITY_BOUNDARY,
                        target_capability=target,
                        rationale="Narrow the candidate's responsibility so it cannot overwrite behavior belonging to the regressed capability.",
                        constraints=("candidate must declare an explicit boundary",),
                    ),
                    BalancingProposal(
                        capability=target,
                        strategy=BalancingStrategy.CONTEXT_ROUTING,
                        target_capability=target,
                        rationale="Condition selection on context when the regression indicates the candidate and baseline may each be valid in different situations.",
                        constraints=("context distinction must be observable",),
                    ),
                )
            )
        return tuple(proposals)
