"""Cognitive build identity and capability manifests.

Software versions describe the implementation package. Cognitive build IDs
identify a reproducible set of capabilities and prevent capability evolution
from becoming an untracked mutable state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CapabilityRecord:
    name: str
    maturity: str
    status: str = "active"

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.maturity.strip():
            raise ValueError("capability name and maturity are required")
        if self.status not in {"active", "candidate", "held", "deprecated"}:
            raise ValueError("invalid capability status")


@dataclass(frozen=True)
class CognitiveBuild:
    """Immutable identity for a cognitive configuration."""

    build_id: str
    software_version: str
    capabilities: tuple[CapabilityRecord, ...]
    parent_build: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.build_id.strip() or not self.software_version.strip():
            raise ValueError("build identity is required")
        if not self.capabilities:
            raise ValueError("a cognitive build must declare capabilities")
        names = [capability.name for capability in self.capabilities]
        if len(names) != len(set(names)):
            raise ValueError("capability names must be unique")

    def active_capabilities(self) -> tuple[CapabilityRecord, ...]:
        return tuple(c for c in self.capabilities if c.status == "active")

    def has_capability(self, name: str) -> bool:
        return any(c.name == name and c.status == "active" for c in self.capabilities)


def create_build(
    build_id: str,
    software_version: str,
    capabilities: Iterable[CapabilityRecord],
    *,
    parent_build: str | None = None,
    notes: str = "",
) -> CognitiveBuild:
    """Create an immutable candidate build manifest; promotion is external."""
    return CognitiveBuild(
        build_id=build_id,
        software_version=software_version,
        capabilities=tuple(capabilities),
        parent_build=parent_build,
        notes=notes,
    )
