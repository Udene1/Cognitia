"""Language-to-cognition structures.

The semantic frame describes what language contains. This module describes what
Cognitia can carry forward into reasoning: goals, constraints, propositions,
entities and required operations. It deliberately preserves candidate status.
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
class CognitiveRepresentation:
    source_text: str
    goals: tuple[CognitiveGoal, ...]
    entities: tuple[str, ...]
    propositions: tuple[str, ...]
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

    statuses = tuple(dict.fromkeys(p.confidence for p in frame.semantic_propositions))
    propositions = tuple(p.text for p in frame.semantic_propositions)
    entities = tuple(dict.fromkeys(entity.text for entity in frame.entities))
    return CognitiveRepresentation(
        source_text=frame.text,
        goals=goals,
        entities=entities,
        propositions=propositions,
        constraints=tuple(constraints),
        epistemic_status=statuses,
        required_answer_elements=answer_elements,
    )
