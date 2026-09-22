""""Conservative identity matching for candidate claims.

Similarity alone is not truth. This layer asks whether two extracted
statements plausibly describe the same proposition so evidence can be grouped
without treating repeated wording as independent confirmation.

Polarity is evidence about a proposition, not part of the proposition's
identity. Therefore positive and negative observations may share an identity
when their semantic content matches, while their polarity remains attached to
the extracted claim and evidence record.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from ..document_claims import ExtractedClaim


@dataclass(frozen=True)
class ClaimIdentity:
    claim_id: str
    canonical_key: str
    matched_claim_ids: tuple[str, ...]
    confidence: float
    basis: tuple[str, ...]


class ClaimIdentityMatcher:
    """Build conservative equivalence groups from explicit claim structure."""

    def match(self, claims: Sequence[ExtractedClaim], *, threshold: float = 0.78) -> tuple[ClaimIdentity, ...]:
        groups: list[list[ExtractedClaim]] = []
        for claim in claims:
            placed = False
            for group in groups:
                score, _ = self.score(claim, group[0])
                if score >= threshold:
                    group.append(claim)
                    placed = True
                    break
            if not placed:
                groups.append([claim])
        return tuple(self._identity(group) for group in groups)

    def score(self, left: ExtractedClaim, right: ExtractedClaim) -> tuple[float, tuple[str, ...]]:
        left_tokens = _semantic_tokens(left.proposition)
        right_tokens = _semantic_tokens(right.proposition)
        if not left_tokens or not right_tokens:
            return 0.0, ()

        overlap = len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))
        entities = _overlap(left.entities, right.entities)
        relations = _overlap(left.relations, right.relations)
        temporal = _overlap(left.temporal_markers, right.temporal_markers)

        # Polarity is deliberately excluded from semantic identity. A positive
        # and negative observation can be competing evidence about one
        # proposition. Temporal disagreement remains an explicit penalty.
        score = 0.45 * overlap + 0.30 * entities + 0.20 * relations + 0.05 * temporal
        if entities == 0 and relations == 0:
            score *= 0.75

        basis = []
        if overlap >= 0.5:
            basis.append("shared_semantic_terms")
        if entities > 0:
            basis.append("shared_entities")
        if relations > 0:
            basis.append("shared_relations")
        if temporal > 0:
            basis.append("shared_temporal_marker")
        if left.temporal_markers and right.temporal_markers and temporal == 0:
            score *= 0.65
            basis.append("temporal_mismatch")
        if left.polarity != right.polarity:
            basis.append("opposite_polarity")

        return round(score, 3), tuple(basis)

    def _identity(self, group: Sequence[ExtractedClaim]) -> ClaimIdentity:
        representative = group[0]
        key = _canonical(representative)
        scores = [self.score(representative, claim)[0] for claim in group[1:]]
        confidence = min(scores, default=1.0)
        basis: set[str] = set()
        for claim in group[1:]:
            _, reasons = self.score(representative, claim)
            basis.update(reasons)
        return ClaimIdentity(
            claim_id=representative.id,
            canonical_key=key,
            matched_claim_ids=tuple(claim.id for claim in group),
            confidence=confidence,
            basis=tuple(sorted(basis)),
        )


_NEGATION = re.compile(
    r"\b(?:does not|did not|do not|is not|are not|was not|were not|has not|have not|had not|cannot|can't|isn't|wasn't|weren't|don't|doesn't|didn't|not|never|no|neither|without)\b",
    re.IGNORECASE,
)


def _semantic_tokens(value: str) -> set[str]:
    """Return proposition tokens while treating polarity as evidence metadata."""
    normalized = _NEGATION.sub(" ", value.lower())
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalized)
        if len(token) > 2
    }


def _overlap(left: Sequence[str], right: Sequence[str]) -> float:
    a = {value.lower() for value in left}
    b = {value.lower() for value in right}
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _canonical(claim: ExtractedClaim) -> str:
    entities = ",".join(sorted(value.lower() for value in claim.entities))
    relations = ",".join(sorted(value.lower() for value in claim.relations))
    tokens = " ".join(sorted(_semantic_tokens(claim.proposition)))
    return f"entities={entities}|relations={relations}|terms={tokens}"
