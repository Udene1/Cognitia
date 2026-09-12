"""Capability-aware cognitive routing.

Routing chooses how Cognitia should attempt a problem. It does not pretend that
an incomplete capability is sufficient: partial substitutions remain explicit
and the resulting conclusion must be qualified by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass

from .capabilities import Capability, CapabilityAvailability, CapabilityAssessment, SelfModel


@dataclass(frozen=True)
class ReasoningRoute:
    """A selected reasoning method and the epistemic condition attached to it."""

    required_capability: str
    method: str
    availability: CapabilityAvailability
    capability: Capability | None = None
    substitution_required: bool = False
    limitation: str | None = None

    @property
    def requires_qualification(self) -> bool:
        return self.availability is not CapabilityAvailability.AVAILABLE or self.substitution_required


class CognitiveRouter:
    """Select a reasoning route from Cognitia's current self-model."""

    def __init__(self, self_model: SelfModel) -> None:
        self.self_model = self_model

    def route(
        self,
        *,
        required_capability: str,
        preferred_method: str,
        fallback_capability: str | None = None,
        fallback_method: str | None = None,
        substitution_note: str | None = None,
    ) -> ReasoningRoute:
        assessment: CapabilityAssessment = self.self_model.assess(required_capability)
        if assessment.availability is CapabilityAvailability.AVAILABLE:
            return ReasoningRoute(
                required_capability=required_capability,
                method=preferred_method,
                availability=assessment.availability,
                capability=assessment.capability,
            )

        if fallback_capability is not None:
            fallback = self.self_model.get(fallback_capability)
            if fallback is not None:
                return ReasoningRoute(
                    required_capability=required_capability,
                    method=fallback_method or fallback_capability,
                    availability=assessment.availability,
                    capability=fallback,
                    substitution_required=True,
                    limitation=substitution_note or (
                        f"{fallback_capability} cannot establish {required_capability}; "
                        "use it only for a qualified approximation or hypothesis."
                    ),
                )

        return ReasoningRoute(
            required_capability=required_capability,
            method=preferred_method,
            availability=assessment.availability,
            substitution_required=False,
            limitation=(
                f"Cognitia does not currently have the required capability: "
                f"{required_capability}."
            ),
        )
