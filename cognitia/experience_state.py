"""Provenance-preserving experience-to-state transition.

The transition deliberately changes active cognition without collapsing
experience into established knowledge or into self/world/other models.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .experience import CognitiveState, EpistemicOutcome, Experience


class ClaimSource(str, Enum):
    EXPERIENCE = "experience"
    UNCERTAINTY = "uncertainty"


@dataclass(frozen=True)
class ExperienceStateTransition:
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
    """Let retrieved experience affect active state while retaining provenance.

    The transition never writes experience into knowledge, self-model, or
    other/world-model collections. A non-refuted experience is represented in
    the dedicated experience collection and remains epistemically unconfirmed.
    A refuted experience is retained as experience plus an uncertainty marker.
    """
    experience_ids = list(state.experience_ids)
    uncertainty = list(state.uncertainty)
    if experience.experience_id not in experience_ids:
        experience_ids.append(experience.experience_id)

    if experience.observed.outcome is EpistemicOutcome.REFUTED:
        marker = f"refuted-experience:{experience.experience_id}"
        if marker not in uncertainty:
            uncertainty.append(marker)
        source = ClaimSource.UNCERTAINTY
        reason = "Refuted experience remains identifiable as experience and contributes uncertainty rather than knowledge."
    else:
        source = ClaimSource.EXPERIENCE
        reason = "Experience changes active state through its own provenance channel and remains subject to epistemic testing."

    resulting = CognitiveState(
        problem=state.problem,
        evidence_ids=state.evidence_ids,
        knowledge_ids=state.knowledge_ids,
        hypothesis_ids=state.hypothesis_ids,
        uncertainty=tuple(uncertainty),
        goal=state.goal,
        experience_ids=tuple(experience_ids),
        self_model_ids=state.self_model_ids,
        other_model_ids=state.other_model_ids,
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
