"""Cross-domain structural pattern transfer.

Transfer is treated as a hypothesis. Cognitia may recognize a structural
pattern from one artifact and adapt it to a new problem, but recognition never
constitutes an answer. The adapted candidate must survive verification in the
new environment before it can be promoted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class StructuralPattern:
    """Language/domain-neutral structure extracted from an artifact."""

    name: str
    features: tuple[str, ...]
    source: str
    epistemic_status: str = "inference"
    confidence: float = 0.0

    def feature_set(self) -> frozenset[str]:
        return frozenset(self.features)


@dataclass(frozen=True)
class TransferCandidate:
    pattern: StructuralPattern
    target_features: tuple[str, ...]
    similarity: float
    adaptation: tuple[str, ...]
    status: str = "candidate"


@dataclass(frozen=True)
class TransferVerification:
    candidate: TransferCandidate
    passed: bool
    observations: tuple[str, ...]
    reason: str


class StructuralTransferEngine:
    """Find, adapt and verify structural analogies without treating analogy as truth."""

    def __init__(self, patterns: Sequence[StructuralPattern] = ()) -> None:
        self._patterns = tuple(patterns)

    @property
    def patterns(self) -> tuple[StructuralPattern, ...]:
        return self._patterns

    def register(self, pattern: StructuralPattern) -> None:
        """Register a pattern only if it has a non-empty structural signature."""
        if not pattern.features:
            raise ValueError("pattern must contain at least one structural feature")
        self._patterns = tuple((*self._patterns, pattern))

    def retrieve(
        self,
        target_features: Sequence[str],
        *,
        minimum_similarity: float = 0.35,
        limit: int = 5,
    ) -> tuple[TransferCandidate, ...]:
        """Retrieve candidate analogies by structural overlap, not vocabulary."""
        if not target_features:
            return ()
        target = frozenset(target_features)
        candidates: list[TransferCandidate] = []
        for pattern in self._patterns:
            similarity = _jaccard(target, pattern.feature_set())
            if similarity < minimum_similarity:
                continue
            adaptation = _adaptation(pattern.feature_set(), target)
            candidates.append(
                TransferCandidate(
                    pattern=pattern,
                    target_features=tuple(target_features),
                    similarity=similarity,
                    adaptation=adaptation,
                )
            )
        candidates.sort(key=lambda item: (-item.similarity, -item.pattern.confidence, item.pattern.name))
        return tuple(candidates[:limit])

    def verify(
        self,
        candidate: TransferCandidate,
        observations: Sequence[Mapping[str, object]],
    ) -> TransferVerification:
        """Verify a transfer against observations supplied by the target environment.

        Each observation must explicitly state whether the adapted prediction
        held. Missing verdicts are not treated as success.
        """
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


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _adaptation(source: frozenset[str], target: frozenset[str]) -> tuple[str, ...]:
    """Describe structural mismatches that must be adapted and tested."""
    missing = sorted(target - source)
    obsolete = sorted(source - target)
    adaptation: list[str] = []
    if missing:
        adaptation.append("introduce target structure: " + ", ".join(missing))
    if obsolete:
        adaptation.append("remove or reinterpret source structure: " + ", ".join(obsolete))
    if not adaptation:
        adaptation.append("direct structural mapping")
    return tuple(adaptation)
