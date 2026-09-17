"""Structured experience signatures derived from the language representation.

The representation abstracts lexical identity while retaining relation direction
and repeated-argument binding. Extracted relations remain candidate evidence;
this module does not assert semantic truth.
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
    binding_pattern: tuple[tuple[str, int, int], ...] = ()


def signature(text: str, *, question: bool | None = None) -> StructuralExperienceSignature:
    return signature_from_frame(build_language_frame(text, question=question))


def signature_from_frame(frame: LanguageFrame) -> StructuralExperienceSignature:
    relations = tuple(_relation_signature(item) for item in frame.relations)
    return StructuralExperienceSignature(relations=relations, question=frame.question, relation_count=len(relations), binding_pattern=_binding_pattern(frame.relations))


def relation_family_matches(left: StructuralRelation, right: StructuralRelation) -> bool:
    """Compare relation family while preserving structural direction."""
    return left.kind == right.kind and left.predicate == right.predicate and left.subject_role == right.subject_role and left.object_role == right.object_role and left.polarity == right.polarity


def structural_signature_matches(left: StructuralExperienceSignature, right: StructuralExperienceSignature) -> bool:
    """Match local relation families plus repeated-argument topology."""
    if len(left.relations) != len(right.relations):
        return False
    if sorted(left.relations, key=_relation_sort_key) != sorted(right.relations, key=_relation_sort_key):
        return False
    return left.binding_pattern == right.binding_pattern


def _relation_sort_key(relation: StructuralRelation) -> tuple[str, str, str, str, str, str]:
    return (relation.kind, relation.predicate, relation.subject_role, relation.object_role, relation.polarity, relation.modality)


def _relation_signature(relation: RelationMention) -> StructuralRelation:
    if relation.kind == "causal":
        subject_role, object_role = "cause", "effect"
    else:
        subject_role, object_role = _argument_role(relation.subject), _argument_role(relation.object)
    return StructuralRelation(kind=relation.kind, predicate=_normalize_predicate(relation.predicate), subject_role=subject_role, object_role=object_role, polarity=relation.polarity, modality=relation.modality)


def _binding_pattern(relations: tuple[RelationMention, ...]) -> tuple[tuple[str, int, int], ...]:
    ids: dict[str, int] = {}
    next_id = 0
    edges: list[tuple[str, int, int]] = []
    for relation in relations:
        subject = _argument_key(relation.subject)
        object_ = _argument_key(relation.object)
        if subject not in ids:
            ids[subject] = next_id
            next_id += 1
        if object_ not in ids:
            ids[object_] = next_id
            next_id += 1
        edges.append((_normalize_predicate(relation.predicate), ids[subject], ids[object_]))
    return tuple(edges)


def _argument_key(value: str | None) -> str:
    if value is None:
        return "<none>"
    value = value.strip().lower()
    return value or "<empty>"


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
