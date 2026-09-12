"""Structural hypothesis space: entities, relations, assumptions and constraints."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class RelationKind(StrEnum):
    DEPENDS_ON = "depends_on"
    CAUSES = "causes"
    CONSTRAINS = "constrains"
    MODULATES = "modulates"
    CORRELATES = "correlates"


@dataclass(frozen=True)
class ModelElement:
    id: str
    kind: str
    value: str


@dataclass(frozen=True)
class ModelRelation:
    source: str
    relation: RelationKind
    target: str


@dataclass(frozen=True)
class StructuralModel:
    id: str
    elements: tuple[ModelElement, ...] = ()
    relations: tuple[ModelRelation, ...] = ()

    def __post_init__(self) -> None:
        ids = {item.id for item in self.elements}
        if len(ids) != len(self.elements):
            raise ValueError("model element ids must be unique")
        if any(r.source not in ids or r.target not in ids for r in self.relations):
            raise ValueError("relations must reference model elements")


@dataclass(frozen=True)
class StructuralAlternative:
    id: str
    source_model: str
    operation: str
    target: str
    changed_structure: str
    epistemic_status: str = "hypothesis"
    novelty_status: str = "unassessed"


class StructuralHypothesisBuilder:
    """Enumerate bounded structural changes without asserting that they are true."""

    def build(self, model: StructuralModel) -> tuple[StructuralAlternative, ...]:
        result: list[StructuralAlternative] = []
        for element in model.elements:
            for operation, structure in (
                ("remove_dependency", f"remove dependencies involving {element.id}"),
                ("add_dependency", f"allow {element.id} to depend on another relevant variable"),
                ("change_constraint", f"relax or change a constraint on {element.id}"),
            ):
                result.append(self._make(model, operation, element.id, structure))
        for relation in model.relations:
            result.append(self._make(
                model,
                "reverse_relation",
                f"{relation.source}->{relation.target}",
                f"test whether {relation.target} {relation.relation.value} {relation.source}",
            ))
        return tuple(result)

    @staticmethod
    def _make(model: StructuralModel, operation: str, target: str, structure: str) -> StructuralAlternative:
        key = f"{model.id}|{operation}|{target}|{structure}"
        return StructuralAlternative(
            id="sa-" + sha256(key.encode()).hexdigest()[:16],
            source_model=model.id,
            operation=operation,
            target=target,
            changed_structure=structure,
        )
