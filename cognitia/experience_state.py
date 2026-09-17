"""Provenance-preserving boundary for experience-derived cognitive state.

This module deliberately does not treat an experience as truth. It allows a
recorded experience to change the state presented to later cognition while
keeping experience-derived claims separate from established knowledge,
self-model claims, other-agent/world-model claims, and uncertainty.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .experience import CognitiveState, EpistemicOutcome, Experience


class ClaimSource(str, Enum):
    EXPERIENCE = "experience"
    KNOWLEDGE = "knowledge"
    SELF_MODEL = "self_model"
    WORLD_MODEL = "world_model"
    UNCERTAINTY = "uncertainty"


@dataclass(frozen=True)
class ExperienceStateTransition:
    """A proposed active-state change caused by consulting an experience."""

    prior_state: CognitiveState
    resulting_state: CognitiveState
    experience_id: str
    changed: bool
    source: ClaimSource
    epistemically_established: bool
    requires_epistemic_test: bool
    reason: str


def apply_experience_to_state(
    state: CognitiveState, experience: Experience
) -> ExperienceStateTransition:
    """Allow experience to affect active state without promoting it to truth.

    The experience contributes an experience-derived hypothesis. It never
    writes into ``knowledge_ids`` and never removes existing uncertainty.
    Every resulting experience-derived claim remains marked for epistemic
    testing. Refuted experience is represented as uncertainty rather than as
    an established claim.
    """
    marker = f"experience:{experience.experience_id}"
    hypothesis_ids = list(state.hypothesis_ids)
    uncertainty = list(state.uncertainty)

    if experience.observed.outcome is EpistemicOutcome.REFUTED:
        marker = f"refuted-experience:{experience.experience_id}"
        if marker not in uncertainty:
            uncertainty.append(marker)
        source = ClaimSource.UNCERTAINTY
        reason = "Refuted experience can alter expectations only by preserving its refutation as uncertainty."
    else:
        if marker not in hypothesis_ids:
            hypothesis_ids.append(marker)
        source = ClaimSource.EXPERIENCE
        reason = "Experience changes active expectations as an experience-derived hypothesis, not as established knowledge."

    resulting = CognitiveState(
        problem=state.problem,
        evidence_ids=state.evidence_ids,
        knowledge_ids=state.knowledge_ids,
        hypothesis_ids=tuple(hypothesis_ids),
        uncertainty=tuple(uncertainty),
        goal=state.goal,
    )

    return ExperienceStateTransition(
        prior_state=state,
        resulting_state=resulting,
        experience_id=experience.experience_id,
        changed=resulting != state,
        source=source,
        epistemically_established=False,
        requires_epistemic_test=True,
        reason=reason,
    )
