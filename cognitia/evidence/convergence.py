"""Evidence convergence without source-counting slop."""
from __future__ import annotations

from dataclasses import dataclass

from .graph import EvidenceGraph
from .model import Claim, EvidenceRecord


@dataclass(frozen=True)
class ConvergenceAssessment:
    claim: Claim
    supporting: tuple[str, ...]
    contradicting: tuple[str, ...]
    unresolved: tuple[str, ...]
    independent_support_groups: int
    independent_contradiction_groups: int
    weighted_support: float
    weighted_contradiction: float
    status: str

    @property
    def independent_net_support(self) -> float:
        return self.weighted_support - self.weighted_contradiction


class EvidenceConvergenceEngine:
    """Assess whether evidence converges while discounting correlated sources."""

    def assess(self, claim: Claim, evidence: tuple[EvidenceRecord, ...]) -> ConvergenceAssessment:
        relevant = tuple(item for item in evidence if item.claim_id == claim.id)
        graph = EvidenceGraph(relevant)
        supporting = tuple(item.id for item in relevant if item.supports is True)
        contradicting = tuple(item.id for item in relevant if item.supports is False)
        unresolved = tuple(item.id for item in relevant if item.supports is None)

        support_groups = self._groups_for(graph, supporting)
        contradiction_groups = self._groups_for(graph, contradicting)
        support = self._weighted_groups(relevant, support_groups, set(supporting))
        contradiction = self._weighted_groups(relevant, contradiction_groups, set(contradicting))

        if not relevant:
            status = "no_evidence"
        elif contradiction > support and contradiction > 0:
            status = "contradicted"
        elif support > contradiction and support > 0:
            status = "supported"
        elif support == contradiction and support > 0:
            status = "conflicted"
        else:
            status = "unresolved"

        return ConvergenceAssessment(
            claim, supporting, contradicting, unresolved,
            len(support_groups), len(contradiction_groups), support, contradiction, status,
        )

    @staticmethod
    def _groups_for(graph: EvidenceGraph, ids: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
        selected = set(ids)
        groups: list[set[str]] = []
        for record in graph.records():
            if record.id not in selected:
                continue
            roots = set(record.provenance_roots)
            overlapping = [group for group in groups if roots & group]
            if not overlapping:
                groups.append(set(roots))
                continue
            merged = set(roots)
            for group in overlapping:
                merged.update(group)
                groups.remove(group)
            groups.append(merged)
        return tuple(tuple(sorted(group)) for group in groups)

    @staticmethod
    def _weighted_groups(
        records: tuple[EvidenceRecord, ...],
        groups: tuple[tuple[str, ...], ...],
        selected: set[str],
    ) -> float:
        """Weight only evidence in the requested polarity.

        A shared upstream root can appear in both supporting and contradicting
        records. It must not lend its reliability to the opposite polarity.
        """
        selected_records = tuple(record for record in records if record.id in selected)
        total = 0.0
        for group in groups:
            roots = set(group)
            reliability = max(
                (record.source.reliability for record in selected_records if roots.intersection(record.provenance_roots)),
                default=0.0,
            )
            total += reliability
        return min(1.0, total)
