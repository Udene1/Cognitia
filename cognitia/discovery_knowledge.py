"""Knowledge promotion policy for discoveries that survive their evidence lifecycle."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .discovery_artifact import DiscoveryArtifact
from .knowledge.model import KnowledgeItem, KnowledgeSource
from .knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore


@dataclass(frozen=True)
class KnowledgePromotionDecision:
    eligible: bool
    reason: str


class DiscoveryKnowledgePromoter:
    """Turns a discovery into durable knowledge only after reproduction/validation."""

    def assess(self, artifact: DiscoveryArtifact, tests: Iterable[KnowledgeTest]) -> KnowledgePromotionDecision:
        tests = tuple(tests)
        if artifact.epistemic_status not in {"supported", "verified"}:
            return KnowledgePromotionDecision(False, "epistemic_status_not_ready")
        if artifact.reproduction_status not in {"reproduced", "independently_reproduced"}:
            return KnowledgePromotionDecision(False, "independent_reproduction_required")
        if not tests:
            return KnowledgePromotionDecision(False, "validation_tests_required")
        if any(not t.passed or t.challenge for t in tests):
            return KnowledgePromotionDecision(False, "validation_challenge_or_failure_present")
        return KnowledgePromotionDecision(True, "survived_validation_and_reproduction")

    def promote(self, store: ValidatedKnowledgeStore, artifact: DiscoveryArtifact,
                proposition: str, source: KnowledgeSource, tests: tuple[KnowledgeTest, ...]) -> None:
        decision = self.assess(artifact, tests)
        if not decision.eligible:
            raise ValueError(decision.reason)
        item = KnowledgeItem("discovery:" + artifact.id, "supports", proposition, source,
                             id="validated:" + artifact.id, scope="validated_discovery")
        store.promote(item, tests)
