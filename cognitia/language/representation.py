"""A language-to-structure boundary for Cognitia.

Cognitia does not treat raw text as its world model. This module creates an
explicit, inspectable intermediate representation: tokens and spans remain
anchored to source text while entities, relations, propositions, modality,
and temporal markers become structured objects. The parser is intentionally
bounded; uncertain parsing remains uncertain rather than being invented.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence


@dataclass(frozen=True)
class TextToken:
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class EntityMention:
    text: str
    start: int
    end: int
    kind: str = "unknown"


@dataclass(frozen=True)
class RelationMention:
    subject: str
    predicate: str
    object: str | None
    confidence: str = "candidate"


@dataclass(frozen=True)
class AnswerContract:
    """What a question appears to require from an answer.

    This is a requirement model, not an answer. ``yes_no`` means the expected
    primary form is binary; ``needs_explanation`` records that a bare value is
    likely inadequate. ``requested_length`` is qualitative and deliberately
    weak: evidence quality can override stylistic brevity.
    """

    answer_kind: str
    requested_length: str
    needs_explanation: bool
    needs_evidence: bool
    needs_uncertainty: bool
    required_elements: tuple[str, ...] = ()


@dataclass(frozen=True)
class LanguageFrame:
    text: str
    tokens: tuple[TextToken, ...]
    entities: tuple[EntityMention, ...]
    relations: tuple[RelationMention, ...]
    propositions: tuple[str, ...]
    modality: tuple[str, ...]
    temporal_markers: tuple[str, ...]
    negated: bool
    question: bool
    answer_contract: AnswerContract | None = None


def build_language_frame(text: str, *, question: bool | None = None) -> LanguageFrame:
    tokens = tuple(TextToken(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", text))
    entities = _entities(text)
    modality = tuple(dict.fromkeys(m.group(0).lower() for m in re.finditer(
        r"\b(?:may|might|could|can|must|should|would|possibly|likely|unlikely|probably|perhaps|maybe)\b",
        text, re.I,
    )))
    temporal = tuple(dict.fromkeys(m.group(0) for m in re.finditer(
        r"\b(?:18|19|20|21)\d{2}\b|\b(?:today|currently|historically|formerly|before|after|during|since|now)\b",
        text, re.I,
    )))
    relations = _relations(text)
    propositions = tuple(dict.fromkeys(r" ".join(text.split()).split(";"))) if text.strip() else ()
    is_question = text.strip().endswith("?") if question is None else question
    return LanguageFrame(
        text=text,
        tokens=tokens,
        entities=entities,
        relations=relations,
        propositions=propositions,
        modality=modality,
        temporal_markers=temporal,
        negated=bool(re.search(r"\b(?:not|never|no|neither|without)\b", text, re.I)),
        question=is_question,
        answer_contract=None,
    )


def _entities(text: str) -> tuple[EntityMention, ...]:
    stop = {"The", "A", "An", "In", "On", "At", "By", "For", "From", "To", "And", "Or", "But", "What", "Why", "How", "Is", "Are", "Was", "Were"}
    mentions: list[EntityMention] = []
    for m in re.finditer(r"\b[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)*\b", text):
        if m.group(0).split()[0] in stop:
            continue
        kind = "proper_noun"
        if re.search(r"\b(?:Empire|Republic|Kingdom|Company|University|River|Sea|Ocean|City|State|Country)\b", m.group(0), re.I):
            kind = "named_place_or_organization"
        mentions.append(EntityMention(m.group(0), m.start(), m.end(), kind))
    return tuple(mentions)


def _relations(text: str) -> tuple[RelationMention, ...]:
    patterns: Sequence[tuple[str, str]] = (
        (r"(?P<s>.+?)\s+(?P<p>is|was|were|are|became|changed|depends on)\s+(?P<o>.+)", "copular_or_state"),
        (r"(?P<s>.+?)\s+(?P<p>caused|causes|contributed to|led to|resulted in|weakened|undermined|destabilized)\s+(?P<o>.+)", "causal"),
    )
    for pattern, kind in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return (RelationMention(
                subject=match.group("s").strip(" ,."),
                predicate=match.group("p").lower(),
                object=match.group("o").strip(" ."),
                confidence="candidate",
            ),)
    return ()
