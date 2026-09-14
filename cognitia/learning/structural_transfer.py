"""Cross-domain structural pattern transfer using roles and relations.

Surface-feature overlap remains a fallback for legacy patterns, but new patterns
carry a relational signature so transfer is driven by structure rather than
vocabulary. Recognition remains a hypothesis and target verification is mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ..logic_ir import LogicModel, LogicTransferCandidate as IRTransferCandidate, LogicTransferEngine


@dataclass(frozen=True)
class StructuralPattern:
    name: str
    features: tuple[str, ...]
    source: str
    epistemic_status: str = "inference"
    confidence: float = 0.0
    logic: LogicModel | None = None

    def feature_set(self) -> frozenset[str]:
        return frozenset(self.features)


@dataclass(frozen=True)
class TransferCandidate:
    pattern: StructuralPattern
    target_features: tuple[str, ...]
    similarity: float
    adaptation: tuple[str, ...]
    status: str = "candidate"
    logic_candidate: IRTransferCandidate | None = None


@dataclass(frozen=True)
class TransferVerification:
    candidate: TransferCandidate
    passed: bool
    observations: tuple[str, ...]
    reason: str


class StructuralTransferEngine:
    """Find, adapt and verify structural analogies without analogy-as-truth."""

    def __init__(self, patterns: Sequence[StructuralPattern] = ()) -> None:
        self._patterns = tuple(patterns)
        self._logic_engine = LogicTransferEngine()

    @property
    def patterns(self) -> tuple[StructuralPattern, ...]:
        return self._patterns

    def register(self, pattern: StructuralPattern) -> None:
        if not pattern.features and pattern.logic is None:
            raise ValueError("pattern must contain structural features or a logic model")
        self._patterns = tuple((*self._patterns, pattern))

    def retrieve(self, target_features: Sequence[str], *, minimum_similarity: float = 0.35, limit: int = 5,
                 target_logic: LogicModel | None = None) -> tuple[TransferCandidate, ...]:
        if not target_features and target_logic is None:
            return ()
        target = frozenset(target_features)
        candidates: list[TransferCandidate] = []
        for pattern in self._patterns:
            logic_candidate = None
            if pattern.logic is not None and target_logic is not None:
                logic_candidate = self._logic_engine.compare(pattern.logic, target_logic)
                similarity = logic_candidate.structural_score
                adaptation = logic_candidate.adaptations
            else:
                similarity = _structural_feature_score(target, pattern.feature_set())
                adaptation = _adaptation(pattern.feature_set(), target)
            if similarity < minimum_similarity:
                continue
            candidates.append(TransferCandidate(pattern, tuple(target_features), similarity, tuple(adaptation), logic_candidate=logic_candidate))
        candidates.sort(key=lambda item: (-item.similarity, -item.pattern.confidence, item.pattern.name))
        return tuple(candidates[:limit])

    def verify(self, candidate: TransferCandidate, observations: Sequence[Mapping[str, object]]) -> TransferVerification:
        if not observations:
            return TransferVerification(candidate, False, (), "no target observations")
        normalized: list[str] = []
        verdicts: list[bool] = []
        for observation in observations:
            verdict = observation.get("verified")
            normalized.append(str(observation.get("description", observation)))
            if isinstance(verdict, bool):
                verdicts.append(verdict)
        if not verdicts:
            return TransferVerification(candidate, False, tuple(normalized), "observations contain no explicit verification verdict")
        if all(verdicts):
            return TransferVerification(candidate, True, tuple(normalized), "all supplied target observations verified the transfer")
        return TransferVerification(candidate, False, tuple(normalized), "at least one supplied target observation falsified the transfer")


def _structural_feature_score(left: frozenset[str], right: frozenset[str]) -> float:
    """Legacy fallback with category-aware weighting, not plain Jaccard."""
    if not left or not right:
        return 0.0
    exact = len(left & right) / max(1, len(left | right))
    categories = {item.split(":", 1)[0] for item in left if ":" in item} & {item.split(":", 1)[0] for item in right if ":" in item}
    category_score = len(categories) / max(1, len({item.split(":", 1)[0] for item in left} | {item.split(":", 1)[0] for item in right}))
    return 0.7 * exact + 0.3 * category_score


def _adaptation(source: frozenset[str], target: frozenset[str]) -> tuple[str, ...]:
    missing = sorted(target - source)
    obsolete = sorted(source - target)
    adaptation: list[str] = []
    if missing:
        adaptation.append("introduce target structure: " + ", ".join(missing))
    if obsolete:
        adaptation.append("remove or reinterpret source structure: " + ", ".join(obsolete))
    return tuple(adaptation or ["direct structural mapping"])
