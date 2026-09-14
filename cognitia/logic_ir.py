"""Representation-neutral logic substrate for cross-domain cognition.

The IR intentionally models invariants rather than surface syntax. Adapters can
project text, code, mathematics, or other observations into the same structure;
transfer then operates on roles and relations and must be verified in the target.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class LogicNode:
    id: str
    role: str
    kind: str
    value: str = ""
    attributes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class LogicRelation:
    source: str
    relation: str
    target: str
    attributes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class LogicModel:
    purpose: str
    nodes: tuple[LogicNode, ...]
    relations: tuple[LogicRelation, ...]
    constraints: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    invariants: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    source_representations: tuple[str, ...] = ()
    confidence: float = 0.0
    provenance: "LogicProvenance | None" = None

    def node(self, node_id: str) -> LogicNode:
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise KeyError(node_id)

    def fingerprint(self) -> str:
        payload = "|".join(
            [self.purpose, *(f"{n.role}:{n.kind}:{n.value}" for n in self.nodes),
             *(f"{r.source}:{r.relation}:{r.target}" for r in self.relations),
             *self.constraints, *self.assumptions, *self.invariants]
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def relation_signature(self) -> tuple[tuple[str, str, str], ...]:
        return tuple(sorted((self.node(r.source).role, r.relation, self.node(r.target).role) for r in self.relations))


@dataclass(frozen=True)
class LogicProvenance:
    source_artifacts: tuple[str, ...]
    observations: tuple[str, ...] = ()
    interpretation: str = ""
    assumptions: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    successful_transfers: tuple[str, ...] = ()
    failed_transfers: tuple[str, ...] = ()

    def with_transfer(self, target_fingerprint: str, *, success: bool) -> "LogicProvenance":
        if success:
            return LogicProvenance(self.source_artifacts, self.observations, self.interpretation,
                                   self.assumptions, self.evidence_ids,
                                   (*self.successful_transfers, target_fingerprint), self.failed_transfers)
        return LogicProvenance(self.source_artifacts, self.observations, self.interpretation,
                               self.assumptions, self.evidence_ids, self.successful_transfers,
                               (*self.failed_transfers, target_fingerprint))


@dataclass(frozen=True)
class TransferMapping:
    source_node: str
    target_node: str
    role_match: float
    relation_support: int


@dataclass(frozen=True)
class LogicTransferCandidate:
    source: LogicModel
    target: LogicModel
    mappings: tuple[TransferMapping, ...]
    structural_score: float
    adaptations: tuple[str, ...]
    status: str = "candidate"


@dataclass(frozen=True)
class LogicTransferVerification:
    candidate: LogicTransferCandidate
    passed: bool
    observations: tuple[str, ...]
    reason: str


class LogicTransferEngine:
    """Transfer relational structure across representations and domains."""

    def compare(self, source: LogicModel, target: LogicModel) -> LogicTransferCandidate:
        mappings: list[TransferMapping] = []
        for target_node in target.nodes:
            compatible = [node for node in source.nodes if node.role == target_node.role]
            if not compatible:
                continue
            best = max(compatible, key=lambda node: _relation_support(source, node.id, target, target_node.id))
            support = _relation_support(source, best.id, target, target_node.id)
            mappings.append(TransferMapping(best.id, target_node.id, 1.0, support))
        relation_overlap = _relation_overlap(source, target, mappings)
        role_coverage = len(mappings) / max(1, len(target.nodes))
        score = 0.6 * role_coverage + 0.4 * relation_overlap
        adaptations = _adaptations(source, target, mappings)
        return LogicTransferCandidate(source, target, tuple(mappings), score, tuple(adaptations))

    def verify(self, candidate: LogicTransferCandidate, observations: Sequence[Mapping[str, object]]) -> LogicTransferVerification:
        if not observations:
            return LogicTransferVerification(candidate, False, (), "no target observations")
        verdicts = [o.get("verified") for o in observations]
        if not all(isinstance(v, bool) for v in verdicts):
            return LogicTransferVerification(candidate, False, tuple(str(o) for o in observations), "every observation requires an explicit boolean verification verdict")
        passed = all(verdicts)
        return LogicTransferVerification(candidate, passed, tuple(str(o.get("description", o)) for o in observations),
                                         "all target observations verified the transfer" if passed else "target evidence falsified the transfer")


def model_from_parts(*, purpose: str, nodes: Iterable[LogicNode], relations: Iterable[LogicRelation],
                     constraints: Iterable[str] = (), assumptions: Iterable[str] = (),
                     invariants: Iterable[str] = (), source_artifacts: Iterable[str] = (),
                     source_representations: Iterable[str] = (), interpretation: str = "") -> LogicModel:
    sources = tuple(source_artifacts)
    return LogicModel(
        purpose=purpose.strip(), nodes=tuple(nodes), relations=tuple(relations),
        constraints=tuple(dict.fromkeys(x.strip() for x in constraints if x.strip())),
        assumptions=tuple(dict.fromkeys(x.strip() for x in assumptions if x.strip())),
        invariants=tuple(dict.fromkeys(x.strip() for x in invariants if x.strip())),
        source_ids=sources, source_representations=tuple(source_representations),
        provenance=LogicProvenance(sources, interpretation=interpretation),
    )


def _relation_support(source: LogicModel, source_id: str, target: LogicModel, target_id: str) -> int:
    source_relations = {r.relation for r in source.relations if r.source == source_id or r.target == source_id}
    target_relations = {r.relation for r in target.relations if r.source == target_id or r.target == target_id}
    return len(source_relations & target_relations)


def _relation_overlap(source: LogicModel, target: LogicModel, mappings: Sequence[TransferMapping]) -> float:
    mapping = {m.source_node: m.target_node for m in mappings}
    source_edges = {(r.source, r.relation, r.target) for r in source.relations if r.source in mapping and r.target in mapping}
    target_edges = {(mapping[r.source], r.relation, mapping[r.target]) for r in source.relations if r.source in mapping and r.target in mapping}
    actual = {(r.source, r.relation, r.target) for r in target.relations}
    return len(target_edges & actual) / max(1, len(actual | target_edges))


def _adaptations(source: LogicModel, target: LogicModel, mappings: Sequence[TransferMapping]) -> list[str]:
    mapped = {m.source_node for m in mappings}
    result: list[str] = []
    if len(mapped) < len(source.nodes):
        result.append("reinterpret source roles absent from target")
    if len(mappings) < len(target.nodes):
        result.append("instantiate target roles without a direct source analogue")
    if source.invariants != target.invariants:
        result.append("check target invariants before execution")
    if source.constraints != target.constraints:
        result.append("reconcile source and target constraints")
    return result or ["direct relational instantiation"]
