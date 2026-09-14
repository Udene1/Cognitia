"""Deterministic document interpretation for Cognitia.

This layer extracts candidate statements from acquired documents. It never
promotes an extracted statement to truth: every candidate retains the source
observation and an explicit confidence/uncertainty label.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Iterable

from .environment import EnvironmentObservation


@dataclass(frozen=True)
class ExtractedClaim:
    id: str
    proposition: str
    observation_id: str
    source: str
    sentence: str
    confidence: str
    temporal_markers: tuple[str, ...] = ()
    entities: tuple[str, ...] = ()
    relations: tuple[str, ...] = ()
    uncertainty_markers: tuple[str, ...] = ()
    polarity: str = "positive"
    attribution_markers: tuple[str, ...] = ()


class DocumentClaimExtractor:
    """Extract bounded, auditable candidate claims without an LLM."""

    _SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
    _TEMPORAL_CONTEXT = re.compile(
        r"\b(?:in|since|from|during|by|after|before)\s+(?:the\s+)?(?:19\d{2}|20\d{2}|\d{4}|\d{1,2}\s+century)\b"
        r"|\b(?:historically|currently|today|now|formerly|originally)\b",
        re.IGNORECASE,
    )
    _YEAR = re.compile(r"\b(?:18|19|20|21)\d{2}\b")
    _UNCERTAIN = re.compile(
        r"\b(?:may|might|could|can|possibly|likely|unlikely|appears|reported|believed|estimated|according to)\b",
        re.IGNORECASE,
    )
    _NEGATION = re.compile(
        r"\b(?:does not|did not|do not|is not|are not|was not|were not|has not|have not|had not|cannot|can't|isn't|wasn't|weren't|don't|doesn't|didn't|not|never|no|neither|without)\b",
        re.IGNORECASE,
    )
    _ATTRIBUTION = re.compile(
        r"\b(?:according to|reported by|reported|believed by|argued by|claimed by|said by|historians? argue|researchers? report|scientists? report)\b",
        re.IGNORECASE,
    )
    _RELATION = re.compile(
        r"\b(?:is|was|were|are|became|changed|defined|redefined|measured|contains|uses|used|causes|caused|produces|depends|disagree|disagrees|contribute|contributed|contributes|led|resulted|weakened|undermined|destabilized)\b",
        re.IGNORECASE,
    )
    _CAUSAL = re.compile(
        r"\b(?:because|because of|due to|caused|causes|contribute|contributed|contributes|led to|resulted in|weakened|undermined|destabilized)\b",
        re.IGNORECASE,
    )
    _ENTITY = re.compile(r"\b[A-Z][A-Za-z0-9-]*\b")
    _ENTITY_STOPWORDS = {"A", "An", "The", "In", "On", "At", "By", "For", "From", "To", "And", "Or", "Some"}

    def extract(self, observation: EnvironmentObservation, *, limit: int = 50) -> tuple[ExtractedClaim, ...]:
        if limit < 1:
            return ()
        candidates: list[ExtractedClaim] = []
        for sentence in self._sentences(observation.content):
            normalized = " ".join(sentence.split())
            if not self._is_claim_candidate(normalized):
                continue
            temporal_values = [m.group(0) for m in self._TEMPORAL_CONTEXT.finditer(normalized)]
            temporal_values.extend(m.group(0) for m in self._YEAR.finditer(normalized))
            temporal = tuple(dict.fromkeys(temporal_values))
            uncertainty = tuple(dict.fromkeys(m.group(0).lower() for m in self._UNCERTAIN.finditer(normalized)))
            attribution = tuple(dict.fromkeys(m.group(0).lower() for m in self._ATTRIBUTION.finditer(normalized)))
            entities = tuple(dict.fromkeys(
                m.group(0) for m in self._ENTITY.finditer(normalized)
                if m.group(0) not in self._ENTITY_STOPWORDS
            ))
            relations = tuple(dict.fromkeys(m.group(0).lower() for m in self._RELATION.finditer(normalized)))
            polarity = "negative" if self._NEGATION.search(normalized) else "positive"
            confidence = "uncertain" if uncertainty else "candidate"
            fingerprint = sha256(f"{observation.id}|{normalized}".encode("utf-8")).hexdigest()[:24]
            candidates.append(ExtractedClaim(
                id=f"claim:{fingerprint}",
                proposition=normalized,
                observation_id=observation.id,
                source=observation.source,
                sentence=normalized,
                confidence=confidence,
                temporal_markers=temporal,
                entities=entities,
                relations=relations,
                uncertainty_markers=uncertainty,
                polarity=polarity,
                attribution_markers=attribution,
            ))
            if len(candidates) >= limit:
                break
        return tuple(candidates)

    def extract_many(self, observations: Iterable[EnvironmentObservation], *, limit_per_document: int = 50) -> tuple[ExtractedClaim, ...]:
        claims: list[ExtractedClaim] = []
        for observation in observations:
            claims.extend(self.extract(observation, limit=limit_per_document))
        return tuple(claims)

    def _sentences(self, content: str) -> Iterable[str]:
        for part in self._SENTENCE.split(content):
            cleaned = " ".join(part.split())
            if cleaned:
                yield cleaned

    def _is_claim_candidate(self, sentence: str) -> bool:
        words = sentence.split()
        return 5 <= len(words) <= 80 and (
            any(token in sentence.lower().split() for token in (
                "is", "was", "were", "are", "became", "changed", "defined", "measured", "uses", "used",
            ))
            or bool(self._UNCERTAIN.search(sentence))
            or bool(self._CAUSAL.search(sentence))
        )
