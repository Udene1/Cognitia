"""Provenance graph for evidence lineage and independence analysis."""
from __future__ import annotations

from dataclasses import dataclass

from .model import EvidenceRecord


@dataclass(frozen=True)
class EvidenceRelation:
    left_id: str
    right_id: str
    relation: str


class EvidenceGraph:
    """In-memory evidence graph; it never promotes claims to knowledge."""

    def __init__(self, evidence: tuple[EvidenceRecord, ...] = ()) -> None:
        self._evidence: dict[str, EvidenceRecord] = {item.id: item for item in evidence}

    def add(self, record: EvidenceRecord) -> None:
        if record.id in self._evidence and self._evidence[record.id] != record:
            raise ValueError(f"evidence id collision: {record.id}")
        self._evidence[record.id] = record

    def get(self, evidence_id: str) -> EvidenceRecord:
        return self._evidence[evidence_id]

    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._evidence[key] for key in sorted(self._evidence))

    def relations(self) -> tuple[EvidenceRelation, ...]:
        records = self.records()
        result: list[EvidenceRelation] = []
        for index, left in enumerate(records):
            for right in records[index + 1:]:
                if left.fingerprint == right.fingerprint:
                    relation = "duplicate"
                elif set(left.provenance_roots) & set(right.provenance_roots):
                    relation = "shared_upstream"
                elif left.source.id == right.source.id:
                    relation = "same_source"
                else:
                    relation = "independent_candidate"
                result.append(EvidenceRelation(left.id, right.id, relation))
        return tuple(result)

    def independent_groups(self, claim_id: str) -> tuple[tuple[str, ...], ...]:
        records = [item for item in self.records() if item.claim_id == claim_id]
        groups: list[set[str]] = []
        for record in records:
            roots = set(record.provenance_roots)
            for group in groups:
                if roots & group:
                    group.update(roots)
                    break
            else:
                groups.append(set(roots))
        return tuple(tuple(sorted(group)) for group in groups)
