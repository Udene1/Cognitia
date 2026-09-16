"""Language -> semantic representation for Cognitia.

Raw language is preserved as evidence. This layer turns it into an explicit,
auditable semantic structure without pretending extraction is truth.
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
class EventMention:
    predicate: str
    participants: tuple[str, ...]
    temporal_markers: tuple[str, ...] = ()
    modality: str = "asserted"
    confidence: str = "candidate"


@dataclass(frozen=True)
class RelationMention:
    subject: str
    predicate: str
    object: str | None
    kind: str = "relation"
    confidence: str = "candidate"
    polarity: str = "positive"
    modality: str = "asserted"
    temporal_markers: tuple[str, ...] = ()
    attribution: str | None = None


@dataclass(frozen=True)
class SemanticProposition:
    """A candidate proposition independent of its original wording."""

    text: str
    relation_indexes: tuple[int, ...]
    event_indexes: tuple[int, ...]
    entity_mentions: tuple[str, ...]
    polarity: str
    modality: str
    temporal_markers: tuple[str, ...]
    attribution: str | None = None
    confidence: str = "candidate"


@dataclass(frozen=True)
class AnswerContract:
    """What a question appears to require from an answer."""

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
    events: tuple[EventMention, ...]
    propositions: tuple[str, ...]
    modality: tuple[str, ...]
    temporal_markers: tuple[str, ...]
    negated: bool
    question: bool
    answer_contract: AnswerContract | None = None
    semantic_propositions: tuple[SemanticProposition, ...] = ()
    negation_markers: tuple[str, ...] = ()
    attribution_markers: tuple[str, ...] = ()
    causal_relations: tuple[RelationMention, ...] = ()


def build_language_frame(text: str, *, question: bool | None = None) -> LanguageFrame:
    normalized = " ".join(text.split())
    tokens = tuple(TextToken(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", text))
    entities = _entities(text)
    modality = _markers(text, r"\b(?:may|might|could|can|must|should|would|possibly|likely|unlikely|probably|perhaps|maybe|reportedly|believed|estimated|alleged)\b")
    temporal = _markers(text, r"\b(?:[1-9]\d{2,3})\b|\b(?:today|currently|historically|formerly|originally|before|after|during|since|until|by|later|earlier|now)\b")
    negation = _markers(text, r"\b(?:does not|did not|do not|is not|are not|was not|were not|has not|have not|had not|cannot|can't|isn't|wasn't|weren't|don't|doesn't|didn't|not|never|no|neither|without)\b")
    attribution = _markers(text, r"\b(?:according to|reported by|reported|believed by|argued by|claimed by|said by|historians? argue|researchers? report|scientists? report)\b")
    relations = _relations(text, temporal, modality, negation, attribution)
    events = tuple(EventMention(r.predicate, tuple(x for x in (r.subject, r.object or "") if x), r.temporal_markers, r.modality) for r in relations if r.kind == "causal")
    causal = tuple(r for r in relations if r.kind == "causal")
    semantic = _semantic_propositions(normalized, entities, relations, events, temporal, modality, negation, attribution)
    is_question = text.strip().endswith("?") if question is None else question
    return LanguageFrame(
        text=text, tokens=tokens, entities=entities, relations=relations, events=events,
        propositions=(normalized,) if normalized else (), modality=modality, temporal_markers=temporal,
        negated=bool(negation), question=is_question, semantic_propositions=semantic,
        negation_markers=negation, attribution_markers=attribution, causal_relations=causal,
    )


def _markers(text: str, pattern: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(m.group(0).lower() if not m.group(0).isdigit() else m.group(0) for m in re.finditer(pattern, text, re.I)))


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


def _relations(text: str, temporal: tuple[str, ...], modality: tuple[str, ...], negation: tuple[str, ...], attribution: tuple[str, ...]) -> tuple[RelationMention, ...]:
    result: list[RelationMention] = []
    stripped = text.strip()

    causal_patterns: Sequence[tuple[str, str, str]] = (
        (r"Why did (?P<effect>.+?)\s+(?:stall|stop|fail|change|decline|rise|fall|collapse|occur|happen|begin|end)\s+(?:after|following)\s+(?P<cause>.+?)[?!.]?$", "caused", "why-after"),
        (r"What caused (?P<effect>.+?)\s+(?:to\s+)?(?P<verb>stall|stop|fail|change|decline|rise|fall|collapse|occur|happen|begin|end)\s*[?!.]?$", "caused", "what-caused"),
        (r"(?P<effect>.+?)\s+(?:stalled|stopped|failed|changed|declined|rose|fell|collapsed)\s+because\s+(?P<cause>.+?)[?!.]?$", "caused", "because"),
        (r"(?P<cause>.+?)\s+(?:caused|led to|resulted in|triggered)\s+(?P<effect>.+?)[?!.]?$", "caused", "explicit-causal"),
    )
    for pattern, predicate, construction in causal_patterns:
        for match in re.finditer(pattern, text, re.I):
            effect = match.group("effect").strip(" ,.")
            cause = match.groupdict().get("cause")
            if cause is None:
                cause = "<unknown-cause>"
            cause = cause.strip(" ,.")
            result.append(RelationMention(
                subject=cause,
                predicate=predicate,
                object=effect,
                kind="causal",
                confidence="candidate",
                polarity="negative" if negation else "positive",
                modality="uncertain" if modality else "asserted",
                temporal_markers=temporal,
                attribution=attribution[-1] if attribution else None,
            ))

    # Generic patterns are useful for non-question statements. Causal questions
    # are already normalized above; parsing them again creates false duplicate edges.
    if not re.match(r"\s*(?:why did|what caused)\b", stripped, re.I):
        patterns: Sequence[tuple[str, str]] = (
            (r"(?P<s>.+?)\s+(?P<p>is|was|were|are|became|changed|depends on)\s+(?P<o>.+)", "state"),
            (r"(?P<s>.+?)\s+(?P<p>caused|causes|contributed to|led to|resulted in|weakened|undermined|destabilized|reduced|increased|affected|influenced|triggered|prevented|enabled|limited|strengthened)\s+(?P<o>.+)", "causal"),
            (r"(?P<s>.+?)\s+(?P<p>defined|redefined|measured|replaced|preceded|followed|supports|contradicts|explains|distinguishes)\s+(?P<o>.+)", "relational"),
        )
        for pattern, kind in patterns:
            for match in re.finditer(pattern, text, re.I):
                result.append(RelationMention(
                    subject=match.group("s").strip(" ,."), predicate=match.group("p").lower(),
                    object=match.group("o").strip(" ."), kind=kind, confidence="candidate",
                    polarity="negative" if negation else "positive", modality="uncertain" if modality else "asserted",
                    temporal_markers=temporal, attribution=attribution[-1] if attribution else None,
                ))

    unique: list[RelationMention] = []
    seen: set[tuple[str, str, str | None, str]] = set()
    for relation in result:
        key = (relation.subject, relation.predicate, relation.object, relation.kind)
        if key not in seen:
            seen.add(key)
            unique.append(relation)
    return tuple(unique)


def _semantic_propositions(text, entities, relations, events, temporal, modality, negation, attribution):
    if not text:
        return ()
    return (SemanticProposition(
        text=text, relation_indexes=tuple(range(len(relations))), event_indexes=tuple(range(len(events))),
        entity_mentions=tuple(entity.text for entity in entities), polarity="negative" if negation else "positive",
        modality="uncertain" if modality else "asserted", temporal_markers=temporal,
        attribution=attribution[-1] if attribution else None,
        confidence="candidate_uncertain" if modality else "candidate",
    ),)
