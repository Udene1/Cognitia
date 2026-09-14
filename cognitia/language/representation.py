"""A language-to-structure boundary for Cognitia.

Cognitia does not treat raw text as its world model. This module creates an
explicit, inspectable intermediate representation: tokens and spans remain
anchored to source text while entities, relations, propositions, modality,
negation, and temporal markers become structured objects. The parser is
intentionally bounded; uncertain parsing remains uncertain rather than being
invented.
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
    polarity: str = "positive"
    modality: str = "asserted"
    temporal_markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class SemanticProposition:
    """A candidate proposition independent of its original sentence wording."""

    text: str
    relation_indexes: tuple[int, ...]
    entity_mentions: tuple[str, ...]
    polarity: str
    modality: str
    temporal_markers: tuple[str, ...]
    confidence: str = "candidate"


@dataclass(frozen=True)
class AnswerContract:
    """What a question appears to require from an answer.

    This is a requirement model, not an answer. A short answer is a target
    shape, not permission to omit information required for a meaningful result.
    """

    answer_kind: str
    requested_length: str
    needs_explanation: bool
    needs_evidence: bool
    needs_uncertainty: bool
    required_elements: tuple[str, ...] = ()
    stopping_conditions: tuple[str, ...] = ()
    bare_answer_sufficient: bool = False
    answer_rationale: str = ""


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
    semantic_propositions: tuple[SemanticProposition, ...] = ()
    negation_markers: tuple[str, ...] = ()


def build_language_frame(text: str, *, question: bool | None = None) -> LanguageFrame:
    normalized = " ".join(text.split())
    tokens = tuple(TextToken(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", text))
    entities = _entities(text)
    modality = tuple(dict.fromkeys(m.group(0).lower() for m in re.finditer(
        r"\b(?:may|might|could|can|must|should|would|possibly|likely|unlikely|probably|perhaps|maybe|reportedly|believed|estimated)\b",
        text, re.I,
    )))
    temporal = tuple(dict.fromkeys(m.group(0) for m in re.finditer(
        r"\b(?:18|19|20|21)\d{2}\b|\b(?:today|currently|historically|formerly|originally|before|after|during|since|until|by|later|earlier|now)\b",
        text, re.I,
    )))
    negation = tuple(dict.fromkeys(m.group(0).lower() for m in re.finditer(
        r"\b(?:does not|did not|do not|is not|are not|was not|were not|has not|have not|had not|cannot|can't|isn't|wasn't|weren't|don't|doesn't|didn't|not|never|no|neither|without)\b",
        text, re.I,
    )))
    relations = _relations(text, temporal, modality, negation)
    propositions = (normalized,) if normalized else ()
    semantic = _semantic_propositions(normalized, entities, relations, temporal, modality, negation)
    is_question = text.strip().endswith("?") if question is None else question
    return LanguageFrame(
        text=text,
        tokens=tokens,
        entities=entities,
        relations=relations,
        propositions=propositions,
        modality=modality,
        temporal_markers=temporal,
        negated=bool(negation),
        question=is_question,
        answer_contract=None,
        semantic_propositions=semantic,
        negation_markers=negation,
    )


def _entities(text: str) -> tuple[EntityMention, ...]:
    stop = {"The", "A", "An", "In", "On", "At", "By", "For", "From", "To", "And", "Or", "But", "What", "Why", "How", "Is", "Are", "Was", "Were", "Some"}
    mentions: list[EntityMention] = []
    for match in re.finditer(r"\b[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)*\b", text):
        if match.group(0).split()[0] in stop:
            continue
        kind = "proper_noun"
        if re.search(r"\b(?:Empire|Republic|Kingdom|Company|University|River|Sea|Ocean|City|State|Country)\b", match.group(0), re.I):
            kind = "named_place_or_organization"
        mentions.append(EntityMention(match.group(0), match.start(), match.end(), kind))
    return tuple(mentions)


def _relations(text: str, temporal: tuple[str, ...], modality: tuple[str, ...], negation: tuple[str, ...]) -> tuple[RelationMention, ...]:
    patterns: Sequence[tuple[str, str]] = (
        (r"(?P<s>.+?)\s+(?P<p>is|was|were|are|became|changed|depends on)\s+(?P<o>.+)", "state"),
        (r"(?P<s>.+?)\s+(?P<p>caused|causes|contributed to|led to|resulted in|weakened|undermined|destabilized|reduced|increased)\s+(?P<o>.+)", "causal"),
        (r"(?P<s>.+?)\s+(?P<p>defined|redefined|measured|replaced|preceded|followed|supports|contradicts|explains)\s+(?P<o>.+)", "relational"),
    )
    result: list[RelationMention] = []
    for pattern, _kind in patterns:
        for match in re.finditer(pattern, text, re.I):
            result.append(RelationMention(
                subject=match.group("s").strip(" ,."),
                predicate=match.group("p").lower(),
                object=match.group("o").strip(" ."),
                confidence="candidate",
                polarity="negative" if negation else "positive",
                modality="uncertain" if modality else "asserted",
                temporal_markers=temporal,
            ))
    return tuple(result)


def _semantic_propositions(
    text: str,
    entities: tuple[EntityMention, ...],
    relations: tuple[RelationMention, ...],
    temporal: tuple[str, ...],
    modality: tuple[str, ...],
    negation: tuple[str, ...],
) -> tuple[SemanticProposition, ...]:
    if not text:
        return ()
    return (SemanticProposition(
        text=text,
        relation_indexes=tuple(range(len(relations))),
        entity_mentions=tuple(entity.text for entity in entities),
        polarity="negative" if negation else "positive",
        modality="uncertain" if modality else "asserted",
        temporal_markers=temporal,
        confidence="candidate_uncertain" if modality else "candidate",
    ),)
