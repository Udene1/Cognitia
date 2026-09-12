"""Generate and apply explicit repair strategies for capability regressions.

A regression is not a deletion command. This module turns the evidence from a
blocked promotion into bounded repair proposals that can be benchmarked again.
Repairs are candidates, never active cognition: they wrap an existing baseline
and candidate implementation behind an explicit routing policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

from .capability_acquisition import AcquisitionMode, CapabilityCandidate
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


@dataclass(frozen=True)
class RepairPolicy:
    """Observable routing rule used to combine a candidate with its baseline."""

    strategy: BalancingStrategy
    select_candidate: Callable[[object], bool]

    def choose(self, value: object, candidate: CapabilityCandidate, baseline: CapabilityCandidate) -> object:
        selected = self.select_candidate(value)
        return (candidate if selected else baseline).execute(value)


class BalancingEngine:
    """Produce deterministic repair hypotheses and bounded repair candidates."""

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

    def repair(
        self,
        proposal: BalancingProposal,
        candidate: CapabilityCandidate,
        baseline: CapabilityCandidate,
        *,
        selector: Callable[[object], bool],
    ) -> CapabilityCandidate:
        """Construct a bounded repair candidate; never mutates either input.

        ``selector`` is intentionally required. Cognitia must have an observable
        basis for routing rather than silently guessing where a capability is safe.
        """
        if candidate.name != proposal.target_capability:
            raise ValueError("candidate capability does not match proposal")
        if baseline.name != proposal.target_capability:
            raise ValueError("baseline capability does not match proposal")
        if not callable(selector):
            raise TypeError("selector must be callable")

        policy = RepairPolicy(proposal.strategy, selector)

        def run(value: object) -> object:
            return policy.choose(value, candidate, baseline)

        return CapabilityCandidate(
            name=proposal.target_capability,
            mode=AcquisitionMode.COMPOSE,
            operations=(baseline.name, candidate.name, proposal.strategy.value),
            implementation=run,
            representation=(
                f"balanced {proposal.target_capability} via {proposal.strategy.value}; "
                "route between baseline and candidate using an explicit observable selector"
            ),
            source_trace_ids=candidate.source_trace_ids,
            code_artifact=candidate.code_artifact,
        )
