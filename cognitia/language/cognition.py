"""Language-to-cognition structures.

The semantic frame describes what language contains. This module describes what
Cognitia can carry forward into reasoning: goals, constraints, propositions,
entities and required operations. It deliberately preserves candidate status
and proposition-level polarity rather than collapsing a whole sentence into a
single global epistemic label.
"""
from __future__ import annotations

from dataclasses import dataclass

from .representation import LanguageFrame, SemanticProposition


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
class CognitiveProposition:
    """A candidate proposition carried into reasoning without truth inflation."""

    text: str
    polarity: str
    modality: str
    temporal_markers: tuple[str, ...] = ()
    attribution: str | None = None
    confidence: str = "candidate"
    relation_indexes: tuple[int, ...] = ()
    event_indexes: tuple[int, ...] = ()


@dataclass(frozen=True)
class CognitiveRepresentation:
    source_text: str
    goals: tuple[CognitiveGoal, ...]
    entities: tuple[str, ...]
    propositions: tuple[CognitiveProposition, ...]
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

    propositions = tuple(_to_cognitive_proposition(p) for p in frame.semantic_propositions)
    statuses = tuple(dict.fromkeys(p.confidence for p in propositions))
    return CognitiveRepresentation(
        source_text=frame.text,
        goals=goals,
        entities=tuple(dict.fromkeys(entity.text for entity in frame.entities)),
        propositions=propositions,
        constraints=tuple(constraints),
        epistemic_status=statuses,
        required_answer_elements=answer_elements,
    )


def _to_cognitive_proposition(proposition: SemanticProposition) -> CognitiveProposition:
    return CognitiveProposition(
        text=proposition.text,
        polarity=proposition.polarity,
        modality=proposition.modality,
        temporal_markers=proposition.temporal_markers,
        attribution=proposition.attribution,
        confidence=proposition.confidence,
        relation_indexes=proposition.relation_indexes,
        event_indexes=proposition.event_indexes,
    )
