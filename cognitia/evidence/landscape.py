"""Synthesize candidate claims into a usable research state."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from .model import Claim, EvidenceRecord
from .utility import EvidenceGap, EvidenceLandscape, EvidenceUtilityEngine


@dataclass(frozen=True)
class ResearchQuestion:
    id: str
    proposition: str
    claim_ids: tuple[str, ...]


@dataclass(frozen=True)
class LandscapeDecision:
    conclusion: str
    confidence: float
    supporting_claims: tuple[str, ...]
    contradicting_claims: tuple[str, ...]
    unresolved_gaps: tuple[EvidenceGap, ...]
    next_action: str


class EvidenceLandscapeEngine:
    """Build a decision state from claims instead of merely listing them."""

    def __init__(self, utility: EvidenceUtilityEngine | None = None) -> None:
        self.utility = utility or EvidenceUtilityEngine()

    def assess(
        self,
        question: ResearchQuestion,
        claims: Sequence[Claim],
        evidence: Sequence[EvidenceRecord],
    ) -> LandscapeDecision:
        selected = tuple(claim for claim in claims if claim.id in set(question.claim_ids))
        landscape: EvidenceLandscape = self.utility.build(selected, evidence)
        supported = tuple(item.claim.id for item in landscape.claims if item.assessment.status == "supported")
        contradicted = tuple(item.claim.id for item in landscape.claims if item.assessment.status == "contradicted")
        conflicted = tuple(item.claim.id for item in landscape.claims if item.assessment.status == "conflicted")

        supported_claims = tuple(item.claim for item in landscape.claims if item.claim.id in supported)
        conflicting_pairs = _contradictory_pairs(supported_claims)
        if conflicting_pairs:
            conflicted = tuple(dict.fromkeys((*conflicted, *(claim.id for pair in conflicting_pairs for claim in pair))))

        if conflicted:
            conclusion = "conflicted"
            confidence = 0.0
            next_action = "run a discriminating investigation against the conflicting claims"
        elif supported and not contradicted:
            conclusion = "supported"
            confidence = _confidence(landscape, supported)
            next_action = "seek an independent challenge before promotion"
        elif contradicted and not supported:
            conclusion = "contradicted"
            confidence = _confidence(landscape, contradicted)
            next_action = "seek an independent supporting test or revise the hypothesis"
        else:
            conclusion = "unresolved"
            confidence = 0.0
            next_action = "acquire evidence targeted at the highest-priority unresolved gap"

        return LandscapeDecision(
            conclusion=conclusion,
            confidence=confidence,
            supporting_claims=supported,
            contradicting_claims=contradicted,
            unresolved_gaps=landscape.gaps,
            next_action=next_action,
        )


def _confidence(landscape: EvidenceLandscape, ids: tuple[str, ...]) -> float:
    values = [item.decision_value for item in landscape.claims if item.claim.id in ids]
    return round(sum(values) / max(1, len(values)), 3)


def _contradictory_pairs(claims: Sequence[Claim]) -> tuple[tuple[Claim, Claim], ...]:
    pairs: list[tuple[Claim, Claim]] = []
    for index, left in enumerate(claims):
        for right in claims[index + 1:]:
            if _opposite_propositions(left.proposition, right.proposition):
                pairs.append((left, right))
    return tuple(pairs)


def _opposite_propositions(left: str, right: str) -> bool:
    negation = re.compile(r"\b(?:not|no|never|without|fails?|failed|doesn['’]t|cannot|can't)\b", re.I)
    left_negative = bool(negation.search(left))
    right_negative = bool(negation.search(right))
    if left_negative == right_negative:
        return False
    left_tokens = set(re.findall(r"[a-z0-9]+", left.lower()))
    right_tokens = set(re.findall(r"[a-z0-9]+", right.lower()))
    negative_tokens = {"not", "no", "never", "without", "fails", "fail", "failed", "doesn", "t", "cannot", "can", "does"}
    left_tokens -= negative_tokens
    right_tokens -= negative_tokens
    overlap = len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))
    return overlap >= 0.55
