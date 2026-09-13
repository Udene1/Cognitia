"""Canonical evidence records. Evidence is not knowledge."""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Mapping


@dataclass(frozen=True)
class EvidenceSource:
    id: str
    kind: str
    name: str
    reliability: float = 0.5
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not self.name or not self.kind:
            raise ValueError("source id, kind and name are required")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("source reliability must be between 0 and 1")


@dataclass(frozen=True)
class SourceLineage:
    source_id: str
    upstream_ids: tuple[str, ...] = ()
    transformation: str = ""

    def roots(self) -> tuple[str, ...]:
        return self.upstream_ids or (self.source_id,)


@dataclass(frozen=True)
class Claim:
    id: str
    proposition: str
    domain: str
    conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.proposition.strip() or not self.domain.strip():
            raise ValueError("claim id, proposition and domain are required")


@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    claim_id: str
    source: EvidenceSource
    content: str
    supports: bool | None
    lineage: SourceLineage | None = None
    observation_id: str | None = None
    measured_at: str | None = None
    method: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not self.claim_id or not self.content.strip():
            raise ValueError("evidence id, claim id and content are required")

    @property
    def fingerprint(self) -> str:
        payload = "|".join((self.claim_id, self.content.strip(), self.method or ""))
        return sha256(payload.encode()).hexdigest()[:24]

    @property
    def provenance_roots(self) -> tuple[str, ...]:
        return self.lineage.roots() if self.lineage else (self.source.id,)
