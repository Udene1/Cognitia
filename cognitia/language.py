"""Deterministic language -> semantic -> question representation.

This is a bounded, auditable linguistic boundary. It does not claim general
natural-language understanding and never promotes extraction to truth.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TextToken:
    text: str
    index: int
    kind: str


@dataclass(frozen=True)
class EntityMention:
    text: str
    kind: str
    token_indexes: tuple[int, ...]
    confidence: str = "candidate"


@dataclass(frozen=True)
class EventMention:
    text: str
    predicate: str
    participants: tuple[str, ...]
    temporal_markers: tuple[str, ...] = ()
    modality: str = "asserted"
    confidence: str = "candidate"


@dataclass(frozen=True)
class RelationMention:
    subject: str
    predicate: str
    object: str
    kind: str = "relation"
    polarity: str = "positive"
    modality: str = "asserted"
    temporal_markers: tuple[str, ...] = ()
    attribution: str | None = None
    confidence: str = "candidate"


@dataclass(frozen=True)
class Proposition:
    text: str
    relations: tuple[RelationMention, ...]
    events: tuple[EventMention, ...]
    entities: tuple[str, ...]
    temporal_markers: tuple[str, ...]
    modality: str
    polarity: str
    attribution: str | None = None
    confidence: str = "candidate"


@dataclass(frozen=True)
class LanguageFrame:
    """Language IR retaining lexical evidence and candidate semantic structure."""

    text: str
    tokens: tuple[TextToken, ...]
    entities: tuple[EntityMention, ...]
    propositions: tuple[Proposition, ...]
    relations: tuple[RelationMention, ...]
    events: tuple[EventMention, ...]
    temporal_markers: tuple[str, ...]
    modality_markers: tuple[str, ...]
    negation_markers: tuple[str, ...]
    attribution_markers: tuple[str, ...]
    causal_relations: tuple[RelationMention, ...]


@dataclass(frozen=True)
class AnswerContract:
    """Semantic specification of what would make an answer satisfactory."""

    answer_kind: str
    requested_length: str
    needs_explanation: bool
    needs_evidence: bool
    required_elements: tuple[str, ...]
    stopping_conditions: tuple[str, ...]
    uncertainty_allowed: bool = True
    direct_answer_required: bool = True


@dataclass(frozen=True)
class QuestionAnalysis:
    text: str
    question_type: str
    contract: AnswerContract
    focus_entities: tuple[str, ...]
    requested_operations: tuple[str, ...]
    propositions: tuple[Proposition, ...]
    subquestions: tuple[str, ...] = ()
    confidence: str = "candidate"


class LanguageAnalyzer:
    _WORD = re.compile(r"\d+(?:\.\d+)?|[A-Za-z][A-Za-z0-9'-]*|[^\w\s]", re.UNICODE)
    _YEAR = re.compile(r"\b(?:18|19|20|21)\d{2}\b")
    _TEMPORAL = re.compile(r"\b(?:today|now|currently|historically|formerly|originally|recently|later|earlier|before|after|during|since|until|by|in)\b", re.I)
    _MODAL = re.compile(r"\b(?:may|might|could|can|possibly|likely|unlikely|probably|perhaps|apparently|reportedly|believed|estimated|alleged)\b", re.I)
    _NEGATION = re.compile(r"\b(?:does not|did not|do not|is not|are not|was not|were not|has not|have not|had not|cannot|can not|not|never|no|neither|without|can't|isn't|wasn't|weren't|don't|doesn't|didn't)\b", re.I)
    _ATTRIBUTION = re.compile(r"\b(?:according to|reported by|reported|believed by|argued by|claimed by|said by|historians? argue|researchers? report|scientists? report)\b", re.I)
    _RELATIONS = {
        "is", "are", "was", "were", "became", "caused", "causes", "causing", "contributed", "contributes",
        "led", "resulted", "weakened", "undermined", "destabilized", "depends", "contains", "uses", "used",
        "defined", "redefined", "measured", "replaced", "preceded", "followed", "increased", "decreased",
        "reduced", "produced", "requires", "supports", "contradicts", "distinguishes", "explains", "works",
        "affected", "influenced", "triggered", "prevented", "enabled", "limited", "strengthened", "changed",
    }
    _CAUSAL = {"caused", "causes", "contributed", "contributes", "led", "resulted", "weakened", "undermined", "destabilized", "affected", "influenced", "triggered", "prevented", "enabled", "limited", "strengthened"}
    _ENTITY_STOP = {"A", "An", "The", "This", "That", "These", "Those", "In", "On", "At", "By", "For", "From", "To", "And", "Or", "Why", "What", "How", "When", "Where", "Who", "Which", "Is", "Are", "Was", "Were"}

    def analyze(self, text: str) -> LanguageFrame:
        normalized = " ".join(text.split())
        tokens = self._tokens(normalized)
        temporal = self._markers(normalized, self._TEMPORAL, years=True)
        modality = self._markers(normalized, self._MODAL)
        negation = self._markers(normalized, self._NEGATION)
        attribution = self._markers(normalized, self._ATTRIBUTION)
        entities = self._entities(tokens)
        propositions = self._propositions(normalized, entities, temporal, modality, negation, attribution)
        relations = tuple(r for p in propositions for r in p.relations)
        events = tuple(e for p in propositions for e in p.events)
        causal = tuple(r for r in relations if r.kind == "causal")
        return LanguageFrame(normalized, tokens, entities, propositions, relations, events, temporal, modality, negation, attribution, causal)

    def question(self, text: str) -> QuestionAnalysis:
        frame = self.analyze(text)
        lowered = " ".join(text.lower().split())
        qtype = self._question_type(lowered)
        subquestions = self._subquestions(text)
        contract = self._answer_contract(qtype, lowered, subquestions)
        operations = list(self._requested_operations(qtype, lowered))
        if len(subquestions) > 1:
            operations.append("satisfy_all_subquestions")
        focus = tuple(entity.text for entity in frame.entities)
        confidence = "candidate" if frame.propositions else "low_structure"
        return QuestionAnalysis(" ".join(text.split()), qtype, contract, focus, tuple(dict.fromkeys(operations)), frame.propositions, subquestions, confidence)

    def _tokens(self, text: str) -> tuple[TextToken, ...]:
        result = []
        for i, match in enumerate(self._WORD.finditer(text)):
            value = match.group(0)
            kind = "number" if value.replace(".", "", 1).isdigit() else "word" if value[0].isalnum() else "punctuation"
            result.append(TextToken(value, i, kind))
        return tuple(result)

    def _entities(self, tokens: tuple[TextToken, ...]) -> tuple[EntityMention, ...]:
        result = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.kind != "word" or not token.text[0].isupper() or token.text in self._ENTITY_STOP:
                i += 1
                continue
            words = [token.text]
            indexes = [token.index]
            j = i + 1
            while j < len(tokens) and tokens[j].kind == "word" and tokens[j].text[0].isupper():
                words.append(tokens[j].text); indexes.append(tokens[j].index); j += 1
            result.append(EntityMention(" ".join(words), "named_entity" if len(words) == 1 else "named_phrase", tuple(indexes)))
            i = j
        return tuple(result)

    def _propositions(self, text, entities, temporal, modality, negation, attribution):
        relations = self._relations(text, entities, temporal, modality, negation, attribution)
        if not relations:
            return ()
        events = tuple(EventMention(r.predicate, r.predicate, tuple(x for x in (r.subject, r.object) if x), r.temporal_markers, r.modality, r.confidence) for r in relations if r.kind == "causal")
        return (Proposition(text, relations, events, tuple(e.text for e in entities), temporal, "uncertain" if modality else "asserted", "negative" if negation else "positive", attribution[-1] if attribution else None, "candidate_uncertain" if modality else "candidate"),)

    def _relations(self, text, entities, temporal, modality, negation, attribution):
        words = re.findall(r"[A-Za-z][A-Za-z0-9'-]*", text)
        result = []
        for i, word in enumerate(words):
            predicate = word.lower()
            if predicate not in self._RELATIONS:
                continue
            before = " ".join(words[max(0, i - 8):i])
            after = " ".join(words[i + 1:i + 9])
            subject = self._nearest_entity(before, entities) or (words[i - 1] if i else "unknown")
            obj = self._nearest_entity(after, entities) or (words[i + 1] if i + 1 < len(words) else "unknown")
            kind = "causal" if predicate in self._CAUSAL else "relation"
            result.append(RelationMention(subject, predicate, obj, kind, "negative" if negation else "positive", "uncertain" if modality else "asserted", temporal, attribution[-1] if attribution else None))
        return tuple(result)

    @staticmethod
    def _nearest_entity(fragment, entities):
        lower = fragment.lower()
        matches = [e.text for e in entities if e.text.lower() in lower]
        return matches[-1] if matches else ""

    @staticmethod
    def _markers(text, pattern, *, years=False):
        values = [m.group(0).lower() for m in pattern.finditer(text)]
        if years:
            values.extend(m.group(0) for m in LanguageAnalyzer._YEAR.finditer(text))
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _subquestions(text):
        parts = re.split(r"\s*(?:,?\s+and\s+|;|\?)\s*", text.strip().rstrip("?"), flags=re.I)
        return tuple(p.strip() + ("?" if p.strip() and not p.strip().endswith("?") else "") for p in parts if p.strip())

    @staticmethod
    def _question_type(text):
        if re.match(r"^(is|are|was|were|do|does|did|can|could|should|will|has|have|had)\b", text): return "yes_no"
        if re.match(r"^why\b", text) or re.search(r"\bwhy\b", text): return "explanation_or_cause"
        if re.match(r"^how\b", text): return "procedure_or_mechanism"
        if re.match(r"^when\b", text): return "time_or_event"
        if re.match(r"^where\b", text): return "location"
        if re.match(r"^who\b", text): return "person_or_agent"
        if re.match(r"^which\b", text): return "selection_or_comparison"
        if re.match(r"^what\b", text): return "definition_or_fact"
        return "open_information"

    @staticmethod
    def _answer_contract(qtype, text, subquestions):
        if qtype == "yes_no": return AnswerContract("yes_no", "short", False, False, ("direct classification",), ("classification justified",), True)
        if qtype == "time_or_event": return AnswerContract("fact_or_date", "short", False, False, ("time or event",), ("requested time/event identified",))
        if qtype == "location": return AnswerContract("location", "short", False, False, ("location",), ("location identified",))
        if qtype == "person_or_agent": return AnswerContract("person_or_agent", "short", False, False, ("person or agent",), ("agent identified",))
        if qtype == "definition_or_fact": return AnswerContract("definition_or_fact", "short_or_moderate", False, False, ("direct answer",), ("concept or fact identified",))
        if qtype == "procedure_or_mechanism": return AnswerContract("mechanism_or_procedure", "moderate", True, False, ("process or mechanism", "key steps or causal relations"), ("mechanism sufficiently explained",))
        if qtype == "selection_or_comparison": return AnswerContract("comparison_or_selection", "moderate", True, False, ("options", "comparison criteria", "conclusion"), ("criteria addressed",))
        if qtype == "explanation_or_cause":
            evidence = any(x in text for x in ("evidence", "proof", "support", "distinguish", "competing"))
            elements = ["causal explanation", "contribution or mechanism"]
            if evidence: elements += ["supporting evidence", "contradicting or distinguishing evidence", "uncertainty"]
            return AnswerContract("explanation", "moderate_or_detailed", True, evidence, tuple(elements), ("major explanatory gaps resolved or explicitly stated",))
        return AnswerContract("open_information", "contextual", True, False, ("directly relevant information",), ("answer sufficient for requested scope",))

    @staticmethod
    def _requested_operations(qtype, text):
        mapping = {
            "yes_no": ("classify_proposition",),
            "explanation_or_cause": ("construct_explanation",),
            "procedure_or_mechanism": ("construct_process_or_mechanism",),
            "selection_or_comparison": ("compare_candidates",),
            "time_or_event": ("identify_temporal_fact",),
            "definition_or_fact": ("identify_fact_or_definition",),
        }
        ops = list(mapping.get(qtype, ("retrieve_or_infer_relevant_information",)))
        if qtype == "explanation_or_cause" and any(x in text for x in ("distinguish", "competing", "versus", "vs")): ops.append("compare_explanations")
        return tuple(ops)


# Backwards-compatible aliases used by the package surface.
Token = TextToken
Entity = EntityMention
SemanticRelation = RelationMention


def build_language_frame(text: str) -> LanguageFrame:
    return LanguageAnalyzer().analyze(text)


def analyze_question(text: str) -> QuestionAnalysis:
    return LanguageAnalyzer().question(text)
