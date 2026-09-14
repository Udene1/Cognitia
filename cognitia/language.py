"""Deterministic language-to-semantics boundary for Cognitia.

This module deliberately does not attempt general natural-language understanding.
It creates an auditable intermediate representation that reasoning systems can
consume: tokens, entities, propositions, relations, temporal/modality signals,
question intent, and an answer contract.

The representation is evidence-bearing rather than truth-bearing. Extracted
relations are candidates and retain confidence so downstream cognition cannot
silently treat linguistic extraction as established knowledge.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Token:
    text: str
    index: int
    kind: str


@dataclass(frozen=True)
class Entity:
    text: str
    kind: str
    token_indexes: tuple[int, ...]
    confidence: str = "candidate"


@dataclass(frozen=True)
class SemanticRelation:
    subject: str
    predicate: str
    object: str
    polarity: str = "positive"
    modality: str = "asserted"
    temporal_markers: tuple[str, ...] = ()
    confidence: str = "candidate"


@dataclass(frozen=True)
class Proposition:
    text: str
    relations: tuple[SemanticRelation, ...]
    entities: tuple[str, ...]
    temporal_markers: tuple[str, ...]
    modality: str
    polarity: str
    confidence: str = "candidate"


@dataclass(frozen=True)
class AnswerContract:
    """What a satisfactory answer must contain, independent of wording."""

    answer_kind: str
    requested_length: str
    needs_explanation: bool
    needs_evidence: bool
    required_elements: tuple[str, ...]
    stopping_conditions: tuple[str, ...]
    uncertainty_allowed: bool = True


@dataclass(frozen=True)
class QuestionAnalysis:
    text: str
    question_type: str
    contract: AnswerContract
    focus_entities: tuple[str, ...]
    requested_operations: tuple[str, ...]
    propositions: tuple[Proposition, ...]
    confidence: str = "candidate"


@dataclass(frozen=True)
class LanguageFrame:
    """Language IR: lexical evidence plus candidate semantic structure."""

    text: str
    tokens: tuple[Token, ...]
    entities: tuple[Entity, ...]
    propositions: tuple[Proposition, ...]
    relations: tuple[SemanticRelation, ...]
    temporal_markers: tuple[str, ...]
    modality_markers: tuple[str, ...]
    negation_markers: tuple[str, ...]


class LanguageAnalyzer:
    _WORD = re.compile(r"\d+(?:\.\d+)?|[A-Za-z][A-Za-z0-9'-]*|[^\w\s]", re.UNICODE)
    _YEAR = re.compile(r"\b(?:18|19|20|21)\d{2}\b")
    _TEMPORAL = re.compile(r"\b(?:today|now|currently|historically|formerly|originally|recently|later|earlier|before|after|during|since|until|by|in)\b", re.I)
    _MODAL = re.compile(r"\b(?:may|might|could|can|possibly|likely|unlikely|probably|perhaps|apparently|reportedly|believed|estimated|alleged)\b", re.I)
    _NEGATION = re.compile(r"\b(?:does not|did not|do not|is not|are not|was not|were not|has not|have not|had not|cannot|can not|not|never|no|neither|without|can't|isn't|wasn't|weren't|don't|doesn't|didn't)\b", re.I)
    _RELATION_WORDS = {
        "is", "are", "was", "were", "became", "caused", "causes", "causing", "contributed", "contributes",
        "led", "resulted", "weakened", "undermined", "destabilized", "depends", "contains", "uses", "used",
        "defined", "redefined", "measured", "replaced", "preceded", "followed", "increased", "decreased",
        "reduced", "produced", "requires", "supports", "contradicts", "distinguishes", "explains", "works",
    }
    _ENTITY_STOP = {"A", "An", "The", "This", "That", "These", "Those", "In", "On", "At", "By", "For", "From", "To", "And", "Or", "Why", "What", "How", "When", "Where", "Who", "Which", "Is", "Are", "Was", "Were"}

    def analyze(self, text: str) -> LanguageFrame:
        normalized = " ".join(text.split())
        tokens = self._tokens(normalized)
        temporal = self._markers(normalized, self._TEMPORAL, include_years=True)
        modality = self._markers(normalized, self._MODAL)
        negation = self._markers(normalized, self._NEGATION)
        entities = self._entities(tokens)
        propositions = self._propositions(normalized, entities, temporal, modality, negation)
        relations = tuple(relation for proposition in propositions for relation in proposition.relations)
        return LanguageFrame(normalized, tokens, entities, propositions, relations, temporal, modality, negation)

    def question(self, text: str) -> QuestionAnalysis:
        frame = self.analyze(text)
        lowered = text.strip().lower()
        qtype = self._question_type(lowered)
        contract = self._answer_contract(qtype, lowered)
        operations = self._requested_operations(qtype, lowered)
        focus = tuple(entity.text for entity in frame.entities)
        return QuestionAnalysis(
            text=" ".join(text.split()),
            question_type=qtype,
            contract=contract,
            focus_entities=focus,
            requested_operations=operations,
            propositions=frame.propositions,
        )

    def _tokens(self, text: str) -> tuple[Token, ...]:
        result: list[Token] = []
        for index, match in enumerate(self._WORD.finditer(text)):
            value = match.group(0)
            kind = "number" if value.replace(".", "", 1).isdigit() else "word" if value[0].isalnum() else "punctuation"
            result.append(Token(value, index, kind))
        return tuple(result)

    def _entities(self, tokens: tuple[Token, ...]) -> tuple[Entity, ...]:
        result: list[Entity] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.kind != "word" or not token.text[0].isupper() or token.text in self._ENTITY_STOP:
                i += 1
                continue
            indexes = [token.index]
            words = [token.text]
            j = i + 1
            while j < len(tokens) and tokens[j].kind == "word" and tokens[j].text[0].isupper():
                words.append(tokens[j].text)
                indexes.append(tokens[j].index)
                j += 1
            value = " ".join(words)
            kind = "organization_or_place" if len(words) > 1 else "named_entity"
            result.append(Entity(value, kind, tuple(indexes)))
            i = j
        return tuple(result)

    def _propositions(self, text: str, entities: tuple[Entity, ...], temporal: tuple[str, ...], modality: tuple[str, ...], negation: tuple[str, ...]) -> tuple[Proposition, ...]:
        relations = self._relations(text, entities, temporal, modality, negation)
        if not relations:
            return ()
        return (Proposition(
            text=text,
            relations=relations,
            entities=tuple(entity.text for entity in entities),
            temporal_markers=temporal,
            modality="uncertain" if modality else "asserted",
            polarity="negative" if negation else "positive",
            confidence="candidate_uncertain" if modality else "candidate",
        ),)

    def _relations(self, text: str, entities: tuple[Entity, ...], temporal: tuple[str, ...], modality: tuple[str, ...], negation: tuple[str, ...]) -> tuple[SemanticRelation, ...]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9'-]*", text)
        result: list[SemanticRelation] = []
        for index, word in enumerate(words):
            predicate = word.lower()
            if predicate not in self._RELATION_WORDS:
                continue
            before = " ".join(words[max(0, index - 5):index])
            after = " ".join(words[index + 1:index + 7])
            subject = self._nearest_entity(before, entities) or (words[index - 1] if index else "unknown")
            object_value = self._nearest_entity(after, entities) or (words[index + 1] if index + 1 < len(words) else "unknown")
            result.append(SemanticRelation(
                subject=subject,
                predicate=predicate,
                object=object_value,
                polarity="negative" if negation else "positive",
                modality="uncertain" if modality else "asserted",
                temporal_markers=temporal,
            ))
        return tuple(result)

    @staticmethod
    def _nearest_entity(fragment: str, entities: tuple[Entity, ...]) -> str:
        lowered = fragment.lower()
        matches = [entity.text for entity in entities if entity.text.lower() in lowered]
        return matches[-1] if matches else ""

    @staticmethod
    def _markers(text: str, pattern: re.Pattern[str], *, include_years: bool = False) -> tuple[str, ...]:
        values = [match.group(0).lower() for match in pattern.finditer(text)]
        if include_years:
            values.extend(match.group(0) for match in LanguageAnalyzer._YEAR.finditer(text))
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _question_type(text: str) -> str:
        if re.match(r"^(is|are|was|were|do|does|did|can|could|should|will|has|have|had)\b", text):
            return "yes_no"
        if re.match(r"^why\b", text) or re.search(r"\bwhy\b", text):
            return "explanation_or_cause"
        if re.match(r"^how\b", text):
            return "procedure_or_mechanism"
        if re.match(r"^when\b", text):
            return "time_or_event"
        if re.match(r"^where\b", text):
            return "location"
        if re.match(r"^who\b", text):
            return "person_or_agent"
        if re.match(r"^which\b", text):
            return "selection_or_comparison"
        if re.match(r"^what\b", text):
            return "definition_or_fact"
        return "open_information"

    @staticmethod
    def _answer_contract(qtype: str, text: str) -> AnswerContract:
        if qtype == "yes_no":
            return AnswerContract("yes_no", "short", False, False, ("direct classification",), ("classification justified by available evidence",))
        if qtype == "time_or_event":
            return AnswerContract("fact_or_date", "short", False, False, ("time or event",), ("requested time/event identified",))
        if qtype == "location":
            return AnswerContract("location", "short", False, False, ("location",), ("location identified",))
        if qtype == "person_or_agent":
            return AnswerContract("person_or_agent", "short", False, False, ("person or agent",), ("agent identified",))
        if qtype == "definition_or_fact":
            return AnswerContract("definition_or_fact", "short_or_moderate", False, False, ("direct answer",), ("concept or fact identified",))
        if qtype == "procedure_or_mechanism":
            return AnswerContract("mechanism_or_procedure", "moderate", True, False, ("process or mechanism", "key steps or causal relations"), ("mechanism sufficiently explained",))
        if qtype == "selection_or_comparison":
            return AnswerContract("comparison_or_selection", "moderate", True, False, ("options", "comparison criteria", "conclusion"), ("comparison criteria addressed",))
        if qtype == "explanation_or_cause":
            evidence = "evidence" in text or "proof" in text or "support" in text or "distinguish" in text
            elements = ["causal explanation", "contribution or mechanism"]
            if evidence:
                elements.extend(("supporting evidence", "contradicting or distinguishing evidence", "uncertainty"))
            return AnswerContract("explanation", "moderate_or_detailed", True, evidence, tuple(elements), ("major explanatory gaps are either resolved or explicitly stated",))
        return AnswerContract("open_information", "contextual", True, False, ("directly relevant information",), ("answer is sufficient for the requested scope",))

    @staticmethod
    def _requested_operations(qtype: str, text: str) -> tuple[str, ...]:
        operations: list[str] = []
        if qtype == "yes_no":
            operations.append("classify_proposition")
        elif qtype == "explanation_or_cause":
            operations.append("construct_explanation")
            if "distinguish" in text or "competing" in text:
                operations.append("compare_explanations")
        elif qtype == "procedure_or_mechanism":
            operations.append("construct_process_or_mechanism")
        elif qtype == "selection_or_comparison":
            operations.append("compare_candidates")
        elif qtype == "time_or_event":
            operations.append("identify_temporal_fact")
        elif qtype == "definition_or_fact":
            operations.append("identify_fact_or_definition")
        else:
            operations.append("retrieve_or_infer_relevant_information")
        return tuple(operations)


def build_language_frame(text: str) -> LanguageFrame:
    return LanguageAnalyzer().analyze(text)


def analyze_question(text: str) -> QuestionAnalysis:
    return LanguageAnalyzer().question(text)
