"""Cross-domain structural transfer as a testable hypothesis generator.

An artifact is reduced to a language/domain-neutral structural signature. Matching
structures generate candidate transfers; they are never treated as answers until
adaptation and verification succeed.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable


@dataclass(frozen=True)
class StructuralSignature:
    source_kind: str
    operations: tuple[str, ...]
    relations: tuple[str, ...]
    entities: tuple[str, ...]
    constraints: tuple[str, ...]
    outcome_shape: str = "unknown"

    @property
    def tokens(self) -> frozenset[str]:
        values = (*self.operations, *self.relations, *self.constraints, self.outcome_shape)
        return frozenset(_tokens(" ".join(values)))


@dataclass(frozen=True)
class TransferCandidate:
    source: StructuralSignature
    target: StructuralSignature
    similarity: float
    shared_structure: tuple[str, ...]
    missing_structure: tuple[str, ...]
    status: str = "candidate"


@dataclass(frozen=True)
class TransferVerification:
    candidate: TransferCandidate
    adapted: bool
    verified: bool
    evidence: tuple[str, ...]
    status: str


class StructuralTransferEngine:
    """Retrieve structural analogies and require verification before acceptance."""

    def retrieve(self, target: StructuralSignature, sources: Iterable[StructuralSignature], *, limit: int = 5) -> tuple[TransferCandidate, ...]:
        candidates: list[TransferCandidate] = []
        for source in sources:
            shared = tuple(sorted(source.tokens & target.tokens))
            union = source.tokens | target.tokens
            similarity = len(shared) / math.sqrt(max(1, len(source.tokens) * len(target.tokens)))
            missing = tuple(sorted(target.tokens - source.tokens))
            if similarity > 0:
                candidates.append(TransferCandidate(source, target, similarity, shared, missing))
        candidates.sort(key=lambda item: (-item.similarity, item.source.source_kind))
        return tuple(candidates[:limit])

    def verify(
        self,
        candidate: TransferCandidate,
        *,
        adapter: callable,
        verifier: callable,
    ) -> TransferVerification:
        """Adapt a candidate to the target and verify its predicted behavior."""
        try:
            adapted = adapter(candidate)
        except Exception as exc:
            return TransferVerification(candidate, False, False, (f"adaptation_failed:{type(exc).__name__}",), "rejected")
        try:
            result = verifier(adapted)
        except Exception as exc:
            return TransferVerification(candidate, True, False, (f"verification_failed:{type(exc).__name__}",), "rejected")
        ok = bool(result)
        evidence = ("held_out_verification_passed",) if ok else ("held_out_verification_failed",)
        return TransferVerification(candidate, True, ok, evidence, "validated_transfer" if ok else "rejected")


def signature_from_language(frame) -> StructuralSignature:
    relations = tuple(f"{r.kind}:{r.predicate}:{r.polarity}:{r.modality}" for r in frame.relations)
    operations = tuple(f"event:{event.predicate}" for event in frame.events)
    constraints = (*frame.modality, *frame.temporal_markers, *frame.negation_markers)
    return StructuralSignature("language", operations, relations, tuple(e.text for e in frame.entities), tuple(constraints))


def _tokens(value: str) -> set[str]:
    stop = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "by", "is", "was", "are", "were"}
    return {item for item in re.findall(r"[a-z0-9_]+", value.lower()) if item not in stop}
