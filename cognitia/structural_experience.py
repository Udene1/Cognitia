"""Structured experience relevance derived from the language representation.

This module deliberately treats extracted relations as candidate evidence. It
normalizes relation family and directional roles without preserving lexical
identity. It does not use raw lexical overlap and does not assert that an
extracted relation is true.
"""
from __future__ import annotations

from dataclasses import dataclass

from .language.representation import LanguageFrame, RelationMention, build_language_frame


@dataclass(frozen=True)
class StructuralRelation:
    kind: str
    predicate: str
    subject_role: str
    object_role: str
    polarity: str
    modality: str


@dataclass(frozen=True)
class StructuralExperienceSignature:
    relations: tuple[StructuralRelation, ...]
    question: bool
    relation_count: int


def signature(text: str, *, question: bool | None = None) -> StructuralExperienceSignature:
    frame = build_language_frame(text, question=question)
    return signature_from_frame(frame)


def signature_from_frame(frame: LanguageFrame) -> StructuralExperienceSignature:
    relations = tuple(_relation_signature(item) for item in frame.relations)
    return StructuralExperienceSignature(relations=relations, question=frame.question, relation_count=len(relations))


def relation_family_matches(left: StructuralRelation, right: StructuralRelation) -> bool:
    """Compare relation family while preserving structural direction."""
    return (
        left.kind == right.kind
        and left.predicate == right.predicate
        and left.subject_role == right.subject_role
        and left.object_role == right.object_role
        and left.polarity == right.polarity
    )


def _relation_signature(relation: RelationMention) -> StructuralRelation:
    if relation.kind == "causal":
        subject_role, object_role = "cause", "effect"
    else:
        subject_role, object_role = _argument_role(relation.subject), _argument_role(relation.object)
    return StructuralRelation(
        kind=relation.kind,
        predicate=_normalize_predicate(relation.predicate),
        subject_role=subject_role,
        object_role=object_role,
        polarity=relation.polarity,
        modality=relation.modality,
    )


def _normalize_predicate(predicate: str) -> str:
    value = predicate.strip().lower()
    if value in {"caused", "causes", "led to", "resulted in", "triggered"}:
        return "caused"
    return value


def _argument_role(value: str | None) -> str:
    if value is None:
        return "none"
    value = value.strip().lower()
    if value == "<unknown-cause>":
        return "unknown"
    if not value:
        return "empty"
    return "argument"
