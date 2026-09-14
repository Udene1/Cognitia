"""Language-to-cognition structures.

The semantic frame describes what language contains. This module describes what
Cognitia can carry forward into reasoning: goals, constraints, propositions,
entities and relations. It deliberately preserves candidate status, polarity,
modality and attribution rather than flattening them into plain text.
"""
from __future__ import annotations

from dataclasses import dataclass

from .representation import LanguageFrame


@dataclass(frozen=True)
class CognitiveGoal:
    operation: str
    target: str
    priority: str = "primary"


@dataclass(frozen=True)
class CognitiveConstraint:
    kind: str
    value: str
    source: str = "language"


@dataclass(frozen=True)
class CognitiveRelation:
    subject: str
    predicate: str
    object: str | None
    kind: str
    polarity: str
    modality: str
    temporal_markers: tuple[str, ...]
    attribution: str | None
    confidence: str


@dataclass(frozen=True)
class CognitiveProposition:
    text: str
    polarity: str
    modality: str
    temporal_markers: tuple[str, ...]
    attribution: str | None
    confidence: str
    relation_indexes: tuple[int, ...]
    event_indexes: tuple[int, ...]


@dataclass(frozen=True)
class CognitiveRepresentation:
    source_text: str
    goals: tuple[CognitiveGoal, ...]
    entities: tuple[str, ...]
    propositions: tuple[str, ...]
    semantic_propositions: tuple[CognitiveProposition, ...]
    relations: tuple[CognitiveRelation, ...]
    constraints: tuple[CognitiveConstraint, ...]
    epistemic_status: tuple[str, ...]
    required_answer_elements: tuple[str, ...]


def build_cognitive_representation(
    frame: LanguageFrame,
    *,
    operations: tuple[str, ...] = (),
    answer_elements: tuple[str, ...] = (),
) -> CognitiveRepresentation:
    """Project semantic language into a reasoning-ready representation."""
    goals = tuple(CognitiveGoal(operation=operation, target=frame.text) for operation in operations)
    constraints: list[CognitiveConstraint] = []
    if frame.negation_markers:
        constraints.append(CognitiveConstraint("negation", ", ".join(frame.negation_markers)))
    if frame.modality:
        constraints.append(CognitiveConstraint("modality", ", ".join(frame.modality)))
    if frame.temporal_markers:
        constraints.append(CognitiveConstraint("temporal", ", ".join(frame.temporal_markers)))
    if frame.attribution_markers:
        constraints.append(CognitiveConstraint("attribution", ", ".join(frame.attribution_markers)))

    relations = tuple(
        CognitiveRelation(
            subject=r.subject,
            predicate=r.predicate,
            object=r.object,
            kind=r.kind,
            polarity=r.polarity,
            modality=r.modality,
            temporal_markers=r.temporal_markers,
            attribution=r.attribution,
            confidence=r.confidence,
        )
        for r in frame.relations
    )
    propositions = tuple(
        CognitiveProposition(
            text=p.text,
            polarity=p.polarity,
            modality=p.modality,
            temporal_markers=p.temporal_markers,
            attribution=p.attribution,
            confidence=p.confidence,
            relation_indexes=p.relation_indexes,
            event_indexes=p.event_indexes,
        )
        for p in frame.semantic_propositions
    )
    statuses = tuple(dict.fromkeys(p.confidence for p in frame.semantic_propositions))
    return CognitiveRepresentation(
        source_text=frame.text,
        goals=goals,
        entities=tuple(dict.fromkeys(entity.text for entity in frame.entities)),
        propositions=tuple(p.text for p in frame.semantic_propositions),
        semantic_propositions=propositions,
        relations=relations,
        constraints=tuple(constraints),
        epistemic_status=statuses,
        required_answer_elements=answer_elements,
    )
