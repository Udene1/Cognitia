"""Evidence-driven control for open-ended research.

The controller deliberately does not prescribe a research sequence. It treats
search actions as candidates, scores them against the evidence already seen,
and records why an action was selected. This is a step toward replacing the
fixed open-research scaffold with cognition that chooses its own next action.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from .document_claims import ExtractedClaim
from .research_search import ResearchSearchPlanner, SearchAction


@dataclass(frozen=True)
class ResearchDecision:
    action: SearchAction
    rationale: str
    expected_information_gain: float


class ResearchActionController:
    """Choose the next research action from the current evidence state."""

    def __init__(self, planner: ResearchSearchPlanner | None = None) -> None:
        self.planner = planner or ResearchSearchPlanner()

    def choose(
        self,
        question: str,
        *,
        claims: Sequence[ExtractedClaim] = (),
        observed_queries: Sequence[str] = (),
        unresolved: Sequence[str] = (),
        max_candidates: int = 8,
    ) -> ResearchDecision | None:
        if not question.strip():
            raise ValueError("question is required")
        if max_candidates < 1:
            raise ValueError("max_candidates must be positive")

        candidates = list(self.planner.plan(question, max_actions=max_candidates).actions)
        contradiction = _has_conflicting_language(claims)
        unresolved_state = bool(unresolved) or not claims
        follow_up = self.planner.follow_up(
            question,
            observed_queries=observed_queries,
            unresolved=unresolved_state,
            contradiction=contradiction,
        )
        if follow_up is not None:
            candidates.append(follow_up)

        used = {query.strip().lower() for query in observed_queries}
        scored: list[tuple[float, SearchAction, str]] = []
        known_terms = _known_terms(claims)
        for action in candidates:
            query_key = action.query.objective.strip().lower()
            if query_key in used:
                continue
            query_terms = {term.strip('"').lower() for term in action.query.terms}
            novelty = len(query_terms - known_terms) / max(1, len(query_terms))
            redundancy = len(query_terms & known_terms) / max(1, len(query_terms))
            conflict_bonus = 0.20 if contradiction and action.purpose in {
                "independent check", "contradiction resolution"
            } else 0.0
            uncertainty_bonus = 0.15 if unresolved_state and action.purpose in {
                "independent check", "uncertainty reduction"
            } else 0.0
            score = action.priority + (0.35 * novelty) - (0.15 * redundancy) + conflict_bonus + uncertainty_bonus
            rationale = _rationale(action, contradiction, unresolved_state, novelty)
            scored.append((score, action, rationale))

        if not scored:
            return None
        score, action, rationale = max(scored, key=lambda item: (item[0], item[1].priority, item[1].query.objective))
        return ResearchDecision(action, rationale, round(max(0.0, min(1.0, score)), 3))


def _known_terms(claims: Sequence[ExtractedClaim]) -> set[str]:
    terms: set[str] = set()
    for claim in claims:
        terms.update(token.lower() for token in re.findall(r"[A-Za-z0-9]+", claim.proposition) if len(token) > 2)
    return terms


def _has_conflicting_language(claims: Sequence[ExtractedClaim]) -> bool:
    positive = False
    negative = False
    for claim in claims:
        lowered = claim.proposition.lower()
        if re.search(r"\b(?:not|no|never|without|cannot|can't|didn't|doesn't|isn't|wasn't)\b", lowered):
            negative = True
        else:
            positive = True
    return positive and negative


def _rationale(action: SearchAction, contradiction: bool, unresolved: bool, novelty: float) -> str:
    reasons: list[str] = []
    if contradiction and action.purpose in {"independent check", "contradiction resolution"}:
        reasons.append("resolve competing evidence")
    if unresolved:
        reasons.append("reduce an unresolved gap")
    if novelty > 0.2:
        reasons.append("introduce less-observed search terms")
    if not reasons:
        reasons.append("explore a high-priority unobserved research facet")
    return "; ".join(reasons)
