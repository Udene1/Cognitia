"""Turn candidate evidence into decision-ready evidence landscapes.

Convergence answers "how much does the evidence support or contradict this
claim?" This module answers the next question: "what does that evidence let
Cognitia do?" It keeps uncertainty explicit and ranks claims, gaps, and tests
without converting evidence directly into truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .convergence import ConvergenceAssessment, EvidenceConvergenceEngine
from .model import Claim, EvidenceRecord


@dataclass(frozen=True)
class EvidenceGap:
    claim_id: str
    reason: str
    priority: float


@dataclass(frozen=True)
class ClaimUtility:
    claim: Claim
    assessment: ConvergenceAssessment
    decision_value: float
    usable: bool
    reason: str


@dataclass(frozen=True)
class EvidenceLandscape:
    claims: tuple[ClaimUtility, ...]
    gaps: tuple[EvidenceGap, ...]
    strongest_support: tuple[str, ...]
    strongest_contradiction: tuple[str, ...]

    def usable_claims(self) -> tuple[ClaimUtility, ...]:
        return tuple(item for item in self.claims if item.usable)


class EvidenceUtilityEngine:
    """Rank candidate evidence by usefulness for reasoning and next action."""

    def __init__(self, convergence: EvidenceConvergenceEngine | None = None) -> None:
        self.convergence = convergence or EvidenceConvergenceEngine()

    def build(
        self,
        claims: Sequence[Claim],
        evidence: Sequence[EvidenceRecord],
    ) -> EvidenceLandscape:
        utilities: list[ClaimUtility] = []
        gaps: list[EvidenceGap] = []
        for claim in claims:
            assessment = self.convergence.assess(claim, tuple(evidence))
            usable, reason = self._usable(assessment)
            value = self._decision_value(assessment)
            utilities.append(ClaimUtility(claim, assessment, value, usable, reason))
            if not usable:
                gaps.append(EvidenceGap(claim.id, reason, round(1.0 - value, 3)))

        ranked = sorted(utilities, key=lambda item: (-item.decision_value, item.claim.id))
        gaps.sort(key=lambda item: (-item.priority, item.claim_id))
        return EvidenceLandscape(
            claims=tuple(ranked),
            gaps=tuple(gaps),
            strongest_support=tuple(item.claim.id for item in ranked if item.assessment.status == "supported"),
            strongest_contradiction=tuple(item.claim.id for item in ranked if item.assessment.status == "contradicted"),
        )

    @staticmethod
    def _usable(assessment: ConvergenceAssessment) -> tuple[bool, str]:
        if assessment.status == "supported":
            return True, "independent evidence currently converges on support"
        if assessment.status == "contradicted":
            return True, "independent evidence currently converges on contradiction"
        if assessment.status == "conflicted":
            return False, "independent evidence remains materially conflicted"
        if assessment.status == "no_evidence":
            return False, "no evidence is available for the claim"
        return False, "evidence is insufficient to establish a directional conclusion"

    @staticmethod
    def _decision_value(assessment: ConvergenceAssessment) -> float:
        total = assessment.weighted_support + assessment.weighted_contradiction
        if total == 0:
            return 0.0
        separation = abs(assessment.weighted_support - assessment.weighted_contradiction) / total
        independence = min(1.0, (assessment.independent_support_groups + assessment.independent_contradiction_groups) / 3.0)
        return round((0.65 * separation) + (0.35 * independence), 3)
