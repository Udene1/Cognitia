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


class DocumentClaimExtractor:
    """Extract bounded, auditable candidate claims without an LLM."""

    _SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
    _TEMPORAL = re.compile(
        r"\b(?:in|since|from|during|by|after|before)\s+(?:the\s+)?(?:19\d{2}|20\d{2}|\d{4}|\d{1,2}\s+century)\b"
        r"|\b(?:19\d{2}|20\d{2})\b|\b(?:historically|currently|today|now|formerly|originally)\b",
        re.IGNORECASE,
    )
    _UNCERTAIN = re.compile(
        r"\b(?:may|might|could|can|possibly|possibly|likely|unlikely|appears|reported|believed|estimated|according to)\b",
        re.IGNORECASE,
    )
    _RELATION = re.compile(
        r"\b(?:is|was|were|are|became|changed|defined|redefined|measured|contains|uses|used|causes|produces|depends)\b",
        re.IGNORECASE,
    )
    _ENTITY = re.compile(r"\b[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*){0,4}\b")

    def extract(self, observation: EnvironmentObservation, *, limit: int = 50) -> tuple[ExtractedClaim, ...]:
        if limit < 1:
            return ()
        candidates: list[ExtractedClaim] = []
        for sentence in self._sentences(observation.content):
            normalized = " ".join(sentence.split())
            if not self._is_claim_candidate(normalized):
                continue
            temporal = tuple(dict.fromkeys(m.group(0) for m in self._TEMPORAL.finditer(normalized)))
            uncertainty = tuple(dict.fromkeys(m.group(0).lower() for m in self._UNCERTAIN.finditer(normalized)))
            entities = tuple(dict.fromkeys(m.group(0) for m in self._ENTITY.finditer(normalized)))
            relations = tuple(dict.fromkeys(m.group(0).lower() for m in self._RELATION.finditer(normalized)))
            confidence = "uncertain" if uncertainty else "candidate"
            fingerprint = sha256(
                f"{observation.id}|{normalized}".encode("utf-8")
            ).hexdigest()[:24]
            candidates.append(
                ExtractedClaim(
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
                )
            )
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

    @staticmethod
    def _is_claim_candidate(sentence: str) -> bool:
        words = sentence.split()
        return 5 <= len(words) <= 80 and any(
            token in sentence.lower().split() for token in ("is", "was", "were", "are", "became", "changed", "defined", "measured", "uses", "used")
        )
