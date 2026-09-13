"""Bounded search over explanatory alternatives.

Search explores hypotheses; it does not assert novelty or truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import log2
from typing import Iterable

from .discovery import ExplanatoryGap
from .discovery_structure import StructuralAlternative, StructuralHypothesisBuilder, StructuralModel
from .learning.hypothesis_search import HypothesisSearchLearner, SearchStrategy
from .memory.experience import Experience


@dataclass(frozen=True)
class SearchCandidate:
    candidate: StructuralAlternative
    search_score: float
    depth: int = 1
    derivation: tuple[str, ...] = ()
    novelty_evidence: str = "unassessed"


@dataclass(frozen=True)
class SearchBudget:
    max_candidates: int = 32
    max_depth: int = 1

    def __post_init__(self) -> None:
        if self.max_candidates < 1 or self.max_depth < 1:
            raise ValueError("search budget must be positive")


class DiscoverySearchEngine:
    """Explore a bounded hypothesis space with explicit derivation traces.

    Multi-step candidates are represented as transformation paths over the same
    starting model. They are hypotheses, not executable model mutations.
    """

    def __init__(self, learner: HypothesisSearchLearner | None = None) -> None:
        self.learner = learner or HypothesisSearchLearner()

    def search(
        self,
        model: StructuralModel,
        *,
        gap: ExplanatoryGap | None = None,
        budget: SearchBudget | None = None,
        experiences: Iterable[Experience] = (),
    ) -> tuple[SearchCandidate, ...]:
        budget = budget or SearchBudget()
        strategies = self.learner.rank(experiences)
        base = StructuralHypothesisBuilder().build(model)
        if not base:
            return ()

        ranked: list[SearchCandidate] = []
        frontier: list[tuple[tuple[StructuralAlternative, ...], float]] = [ ((), 0.0) ]
        visited: set[str] = {model.id}
        for depth in range(1, budget.max_depth + 1):
            next_frontier: list[tuple[tuple[StructuralAlternative, ...], float]] = []
            for trace, score in frontier:
                for alternative in base:
                    if alternative in trace:
                        continue
                    new_trace = trace + (alternative,)
                    fingerprint = self._path_fingerprint(model, new_trace)
                    if fingerprint in visited:
                        continue
                    visited.add(fingerprint)
                    new_score = score + self._score(alternative, strategies) / depth
                    candidate = self._path_candidate(model, new_trace, new_score, depth, gap)
                    ranked.append(candidate)
                    next_frontier.append((new_trace, new_score))
                    if len(ranked) >= budget.max_candidates:
                        break
                if len(ranked) >= budget.max_candidates:
                    break
            frontier = next_frontier
            if not frontier or len(ranked) >= budget.max_candidates:
                break
        return tuple(sorted(ranked, key=lambda item: (-item.search_score, item.depth, item.candidate.id)))[:budget.max_candidates]

    @staticmethod
    def _path_fingerprint(model: StructuralModel, trace: tuple[StructuralAlternative, ...]) -> str:
        payload = model.id + "|" + "|".join(item.id for item in trace)
        return sha256(payload.encode()).hexdigest()[:24]

    @classmethod
    def _path_candidate(
        cls, model: StructuralModel, trace: tuple[StructuralAlternative, ...], score: float,
        depth: int, gap: ExplanatoryGap | None,
    ) -> SearchCandidate:
        last = trace[-1]
        cid = "path-" + cls._path_fingerprint(model, trace)[:16]
        alternative = StructuralAlternative(
            id=cid,
            source_model=model.id,
            operation="compose:" + "+".join(item.operation for item in trace),
            target=last.target,
            changed_structure=" then ".join(item.changed_structure for item in trace),
            epistemic_status="hypothesis",
            novelty_status="unassessed",
        )
        return SearchCandidate(
            candidate=alternative,
            search_score=score,
            depth=depth,
            derivation=tuple(item.id for item in trace),
            novelty_evidence="candidate-diff-from-current-model" if gap is not None else "unassessed",
        )

    @staticmethod
    def _score(item: StructuralAlternative, strategies: tuple[SearchStrategy, ...]) -> float:
        operation = item.operation
        for strategy in strategies:
            if strategy.transform.value in operation or DiscoverySearchEngine._transform_operation(strategy.transform.value) == operation:
                return strategy.success_rate * (1.0 + min(strategy.observations, 10) / 10.0)
        return 0.0

    @staticmethod
    def _transform_operation(transform: str) -> str:
        return {
            "add_missing_variable": "add_dependency",
            "relax_assumption": "change_constraint",
            "reverse_assumption": "reverse_relation",
            "partition_context": "add_dependency",
        }.get(transform, transform)


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
