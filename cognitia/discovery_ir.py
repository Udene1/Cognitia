"""Canonical structural representation used to compare discovery candidates."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .discovery_structure import RelationKind, StructuralModel


@dataclass(frozen=True)
class IRNode:
    kind: str
    role: str


@dataclass(frozen=True)
class IRRelation:
    relation: RelationKind
    source_role: str
    target_role: str


@dataclass(frozen=True)
class DiscoveryIR:
    """Normalized structure with identifiers removed from semantic comparison."""

    nodes: tuple[IRNode, ...]
    relations: tuple[IRRelation, ...]

    @property
    def fingerprint(self) -> str:
        payload = repr((self.nodes, self.relations)).encode()
        return sha256(payload).hexdigest()[:24]


class DiscoveryIRBuilder:
    """Normalize a structural model while preserving relation semantics."""

    def build(self, model: StructuralModel) -> DiscoveryIR:
        by_id = {element.id: element for element in model.elements}
        ordered = sorted(model.elements, key=lambda item: (item.kind, item.value, item.id))
        role_by_id = {element.id: f"{element.kind}:{index}" for index, element in enumerate(ordered)}
        nodes = tuple(IRNode(kind=element.kind, role=role_by_id[element.id]) for element in ordered)
        relations = tuple(
            sorted(
                (
                    IRRelation(
                        relation=item.relation,
                        source_role=role_by_id[item.source],
                        target_role=role_by_id[item.target],
                    )
                    for item in model.relations
                    if item.source in by_id and item.target in by_id
                ),
                key=lambda item: (item.relation.value, item.source_role, item.target_role),
            )
        )
        return DiscoveryIR(nodes=nodes, relations=relations)

    def similarity(self, left: DiscoveryIR, right: DiscoveryIR) -> float:
        """Return structural overlap; this is evidence, not semantic equivalence."""
        node_left = set(left.nodes)
        node_right = set(right.nodes)
        relation_left = set(left.relations)
        relation_right = set(right.relations)
        node_union = node_left | node_right
        relation_union = relation_left | relation_right
        node_score = len(node_left & node_right) / len(node_union) if node_union else 1.0
        relation_score = len(relation_left & relation_right) / len(relation_union) if relation_union else 1.0
        return (node_score + relation_score) / 2.0
