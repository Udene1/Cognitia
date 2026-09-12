"""Evidence-backed updates to Cognitia's model of its own capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite

from .capabilities import Capability, SelfModel


@dataclass(frozen=True)
class CapabilityOutcome:
    """Observed result of using a capability on a task."""

    capability: str
    successful: bool
    context: str = ""
    failure_mode: str | None = None

    def __post_init__(self) -> None:
        if not self.capability.strip():
            raise ValueError("capability cannot be empty")
        if not self.successful and self.failure_mode is None:
            raise ValueError("a failed capability outcome must record a failure mode")


@dataclass
class CapabilityHistory:
    """Small empirical history used to revise self-model reliability."""

    outcomes: dict[str, list[CapabilityOutcome]] = field(default_factory=dict)

    def record(self, outcome: CapabilityOutcome) -> None:
        self.outcomes.setdefault(outcome.capability, []).append(outcome)

    def success_rate(self, capability: str) -> float | None:
        entries = self.outcomes.get(capability, [])
        if not entries:
            return None
        return sum(entry.successful for entry in entries) / len(entries)

    def failure_modes(self, capability: str) -> tuple[str, ...]:
        modes = {
            entry.failure_mode
            for entry in self.outcomes.get(capability, [])
            if entry.failure_mode
        }
        return tuple(sorted(modes))


def update_self_model(
    model: SelfModel,
    history: CapabilityHistory,
    capability_name: str,
) -> Capability | None:
    """Revise reliability from observed performance without pretending certainty.

    The observed empirical rate becomes the current reliability estimate only
    when there is history. This is deliberately simple; later builds can add
    uncertainty intervals, context conditioning, sample weighting, and decay.
    """
    capability = model.get(capability_name)
    rate = history.success_rate(capability_name)
    if capability is None or rate is None:
        return capability
    if not isfinite(rate):
        raise ValueError("computed success rate must be finite")

    failures = history.failure_modes(capability_name)
    revised = Capability(
        name=capability.name,
        domain=capability.domain,
        reliability=rate,
        maturity=capability.maturity,
        limitations=capability.limitations,
        failure_modes=tuple(sorted(set(capability.failure_modes).union(failures))),
    )
    model.register(revised)
    return revised
