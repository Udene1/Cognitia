"""Experiment-only bridge from experience evidence to action selection.

This module deliberately does not encode a scenario -> action mapping. It
provides a generic candidate-action selector so the experience blindspot
experiment can measure whether prior experience influences a choice and
whether contradictory experience weakens that influence.

It is a research mechanism, not evidence of cognition or learning.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from .experience import EpistemicOutcome, Experience, ExperienceLedger
from .research_search import SearchAction

_TOKEN = re.compile(r"[a-z0-9_]+")


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
    """Rank existing action candidates using experience as defeasible evidence."""

    def select(
        self,
        problem: str,
        actions: Sequence[SearchAction],
        ledger: ExperienceLedger,
    ) -> ExperienceActionDecision:
        if not problem.strip():
            raise ValueError("problem is required")
        if not actions:
            raise ValueError("at least one action is required")

        problem_terms = _terms(problem)
        experiences = ledger.all()
        assessments: list[ExperienceActionAssessment] = []
        for action in actions:
            action_terms = _terms(action.query.objective)
            candidates = tuple(
                item for item in experiences
                if _relevance(problem_terms, item) > 0
            )
            score = action.priority
            contributions: list[str] = []
            for experience in candidates:
                overlap = _relevance(problem_terms, experience)
                if not overlap:
                    continue
                action_overlap = len(set(action_terms) & _terms(experience.action))
                # Experience is evidence about applicability, not an instruction
                # to repeat the old action. Its contribution is based on the
                # current problem/action relationship and epistemic outcome.
                contribution = 0.20 * overlap
                if experience.observed.outcome is EpistemicOutcome.REFUTED:
                    contribution *= -1.0
                elif experience.observed.outcome is EpistemicOutcome.PARTIAL:
                    contribution *= 0.5
                elif experience.observed.outcome is EpistemicOutcome.UNRESOLVED:
                    contribution *= 0.25
                contribution += 0.05 * action_overlap
                score += contribution
                contributions.append(
                    f"{experience.experience_id}:{contribution:+.3f}:{experience.observed.outcome.value}"
                )
            rationale = "experience candidates=" + (", ".join(contributions) if contributions else "none")
            assessments.append(ExperienceActionAssessment(action, round(score, 6), tuple(item.experience_id for item in candidates), rationale))

        ranked = tuple(sorted(assessments, key=lambda item: (-item.score, item.action.query.objective)))
        return ExperienceActionDecision(ranked[0], ranked)


def _terms(value: str) -> set[str]:
    return {token for token in _TOKEN.findall(value.lower()) if len(token) > 2}


def _relevance(problem_terms: set[str], experience: Experience) -> float:
    prior_terms = _terms(experience.prior_state.problem)
    if not prior_terms:
        return 0.0
    return len(problem_terms & prior_terms) / len(prior_terms)
