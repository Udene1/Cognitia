"""Generic experiment boundary for experience-conditioned action selection.

The selector consumes state-generated actions rather than a researcher-authored
scenario -> action mapping. Experience contributes only defeasible evidence
based on structural state overlap and operation overlap.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .experience import EpistemicOutcome, Experience, ExperienceLedger, CognitiveState
from .state_action_generation import GeneratedAction


@dataclass(frozen=True)
class ExperienceGeneratedActionAssessment:
    action: GeneratedAction
    score: float
    relevant_experience_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ExperienceGeneratedActionDecision:
    selected: ExperienceGeneratedActionAssessment
    candidates: tuple[ExperienceGeneratedActionAssessment, ...]


class ExperienceGeneratedActionSelector:
    """Rank generated actions while treating experience as defeasible evidence."""

    def select(
        self,
        state: CognitiveState,
        actions: Sequence[GeneratedAction],
        ledger: ExperienceLedger,
    ) -> ExperienceGeneratedActionDecision:
        if not actions:
            raise ValueError("at least one generated action is required")

        assessments: list[ExperienceGeneratedActionAssessment] = []
        for action in actions:
            matches = tuple(item for item in ledger.all() if _state_similarity(state, item.prior_state) > 0)
            score = 0.0
            contributions: list[str] = []
            for experience in matches:
                similarity = _state_similarity(state, experience.prior_state)
                capability_overlap = _capability_overlap(action.operation.capability, experience.action)
                if capability_overlap == 0:
                    continue
                contribution = 0.5 * similarity * capability_overlap
                if experience.observed.outcome is EpistemicOutcome.REFUTED:
                    contribution *= -1.0
                elif experience.observed.outcome is EpistemicOutcome.PARTIAL:
                    contribution *= 0.5
                elif experience.observed.outcome is EpistemicOutcome.UNRESOLVED:
                    contribution *= 0.25
                score += contribution
                contributions.append(f"{experience.experience_id}:{contribution:+.3f}:{experience.observed.outcome.value}")
            assessments.append(
                ExperienceGeneratedActionAssessment(
                    action=action,
                    score=round(score, 6),
                    relevant_experience_ids=tuple(item.experience_id for item in matches),
                    rationale="experience=" + (", ".join(contributions) if contributions else "none"),
                )
            )

        ranked = tuple(
            sorted(
                assessments,
                key=lambda item: (-item.score, item.action.operation.name, item.action.objective),
            )
        )
        return ExperienceGeneratedActionDecision(selected=ranked[0], candidates=ranked)


def _state_similarity(current: CognitiveState, prior: CognitiveState) -> float:
    """Compare structural state signals; problem wording is intentionally ignored."""
    matches = 0
    dimensions = 0
    for left, right in (
        (set(current.evidence_ids), set(prior.evidence_ids)),
        (set(current.knowledge_ids), set(prior.knowledge_ids)),
        (set(current.hypothesis_ids), set(prior.hypothesis_ids)),
        (set(current.uncertainty), set(prior.uncertainty)),
    ):
        dimensions += 1
        if left == right:
            matches += 1
    if current.goal is not None or prior.goal is not None:
        dimensions += 1
        if (current.goal or "").strip().lower() == (prior.goal or "").strip().lower():
            matches += 1
    return matches / dimensions if dimensions else 0.0


def _capability_overlap(capability: str, action: str) -> float:
    capability_terms = {part for part in capability.lower().replace("-", " ").split() if part}
    action_terms = {part for part in action.lower().replace("-", " ").split() if part}
    return 1.0 if capability_terms.intersection(action_terms) else 0.0
