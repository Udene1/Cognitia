"""Experiment-only bridge from experience evidence to action selection.

Experience applicability is derived from Cognitia's structured language
representation rather than lexical token overlap. Extracted relations remain
candidate evidence; this module does not claim semantic understanding.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .experience import EpistemicOutcome, ExperienceLedger
from .research_search import SearchAction
from .structural_experience import StructuralExperienceSignature, relation_family_matches, signature, structural_signature_matches


@dataclass(frozen=True)
class ExperienceActionAssessment:
    action: SearchAction
    score: float
    relevant_experience_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ExperienceActionDecision:
    selected: ExperienceActionAssessment
    candidates: tuple[ExperienceActionAssessment, ...]


class ExperienceAwareActionSelector:
    """Rank existing action candidates using structured experience evidence."""

    def select(self, problem: str, actions: Sequence[SearchAction], ledger: ExperienceLedger) -> ExperienceActionDecision:
        if not problem.strip():
            raise ValueError("problem is required")
        if not actions:
            raise ValueError("at least one action is required")

        problem_signature = signature(problem)
        experiences = ledger.all()
        assessments: list[ExperienceActionAssessment] = []
        for action in actions:
            action_signature = signature(action.query.objective)
            candidates = tuple(item for item in experiences if _structural_relevance(problem_signature, signature(item.prior_state.problem)) > 0)
            score = action.priority
            contributions: list[str] = []
            for experience in candidates:
                relevance = _structural_relevance(problem_signature, signature(experience.prior_state.problem))
                if not relevance:
                    continue
                action_match = _structural_action_match(action_signature, signature(experience.action))
                contribution = 0.20 * relevance + 0.05 * action_match
                if experience.observed.outcome is EpistemicOutcome.REFUTED:
                    contribution *= -1.0
                elif experience.observed.outcome is EpistemicOutcome.PARTIAL:
                    contribution *= 0.5
                elif experience.observed.outcome is EpistemicOutcome.UNRESOLVED:
                    contribution *= 0.25
                score += contribution
                contributions.append(f"{experience.experience_id}:{contribution:+.3f}:{experience.observed.outcome.value}")
            rationale = "structured experience candidates=" + (", ".join(contributions) if contributions else "none")
            assessments.append(ExperienceActionAssessment(action, round(score, 6), tuple(item.experience_id for item in candidates), rationale))

        ranked = tuple(sorted(assessments, key=lambda item: (-item.score, item.action.query.objective)))
        return ExperienceActionDecision(ranked[0], ranked)


def _structural_relevance(problem: StructuralExperienceSignature, experience: StructuralExperienceSignature) -> float:
    if not problem.relations or not experience.relations:
        return 0.0
    # Once a state contains multiple relations, local family overlap is not
    # sufficient: repeated-argument topology is part of the experience.
    if len(problem.relations) > 1 or len(experience.relations) > 1:
        return 1.0 if structural_signature_matches(problem, experience) else 0.0
    matches = sum(any(relation_family_matches(left, right) for right in experience.relations) for left in problem.relations)
    return matches / len(problem.relations)


def _structural_action_match(action: StructuralExperienceSignature, experienced_action: StructuralExperienceSignature) -> float:
    if not action.relations or not experienced_action.relations:
        return 0.0
    matches = sum(any(relation_family_matches(left, right) for right in experienced_action.relations) for left in action.relations)
    return matches / len(action.relations)
