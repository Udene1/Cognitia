"""Bounded search over explanatory alternatives.

Search ranks possibilities; it does not turn an unseen candidate into a novelty claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log2

from .discovery import ExplanatoryGap, HypothesisCandidate
from .discovery_structure import StructuralAlternative, StructuralHypothesisBuilder, StructuralModel
from .learning.hypothesis_search import HypothesisSearchLearner


@dataclass(frozen=True)
class SearchCandidate:
    candidate: StructuralAlternative
    search_score: float
    novelty_evidence: str = "unassessed"


@dataclass(frozen=True)
class SearchBudget:
    max_candidates: int = 32
    max_depth: int = 1

    def __post_init__(self) -> None:
        if self.max_candidates < 1 or self.max_depth < 1:
            raise ValueError("search budget must be positive")


class DiscoverySearchEngine:
    """Explore a bounded structural neighborhood and rank it by learned utility."""

    def __init__(self, learner: HypothesisSearchLearner | None = None) -> None:
        self.learner = learner or HypothesisSearchLearner()

    def search(
        self,
        model: StructuralModel,
        *,
        gap: ExplanatoryGap | None = None,
        budget: SearchBudget | None = None,
    ) -> tuple[SearchCandidate, ...]:
        budget = budget or SearchBudget()
        if budget.max_depth != 1:
            raise ValueError("multi-step structural search is not implemented yet")

        strategies = {item.transform: item for item in self.learner.rank()}
        alternatives = StructuralHypothesisBuilder().build(model)[: budget.max_candidates]
        ranked = [
            SearchCandidate(
                candidate=item,
                search_score=self._score(item, strategies),
                novelty_evidence=self._novelty_evidence(item, gap),
            )
            for item in alternatives
        ]
        return tuple(sorted(ranked, key=lambda item: (-item.search_score, item.candidate.id)))

    @staticmethod
    def _score(item: StructuralAlternative, strategies: dict[str, object]) -> float:
        learned = strategies.get(item.operation)
        if learned is None:
            return 0.0
        observations = getattr(learned, "observations", 0)
        success_rate = getattr(learned, "success_rate", 0.0)
        return float(success_rate) * (1.0 + min(observations, 10) / 10.0)

    @staticmethod
    def _novelty_evidence(item: StructuralAlternative, gap: ExplanatoryGap | None) -> str:
        if gap is None:
            return "unassessed"
        if item.operation in {"change_constraint", "add_dependency", "remove_dependency", "reverse_relation"}:
            return "candidate-diff-from-current-model"
        return "unassessed"


def normalized_entropy(probabilities: tuple[float, ...]) -> float:
    """Calculate Shannon entropy in bits for a valid probability distribution."""
    if not probabilities:
        raise ValueError("probability distribution cannot be empty")
    if any(value < 0 for value in probabilities):
        raise ValueError("probabilities cannot be negative")
    total = sum(probabilities)
    if total <= 0 or abs(total - 1.0) > 1e-9:
        raise ValueError("probabilities must sum to one")
    return -sum(value * log2(value) for value in probabilities if value > 0)
