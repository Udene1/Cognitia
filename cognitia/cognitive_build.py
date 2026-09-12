"""Immutable manifests for reproducible Cognitia cognitive builds."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CapabilityState(str, Enum):
    ACTIVE = "active"
    CANDIDATE = "candidate"
    HELD = "held"
    DEPRECATED = "deprecated"


@dataclass(frozen=True)
class CapabilityManifest:
    name: str
    state: CapabilityState
    reliability: float
    source_build: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("capability name cannot be empty")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be between 0 and 1")


@dataclass(frozen=True)
class CognitiveBuild:
    """A named, reproducible snapshot of Cognitia's cognitive machinery."""

    build_id: str
    software_version: str
    capabilities: tuple[CapabilityManifest, ...]
    parent_build: str | None = None

    def __post_init__(self) -> None:
        if not self.build_id.strip() or not self.software_version.strip():
            raise ValueError("build_id and software_version are required")
        names = [c.name for c in self.capabilities]
        if len(names) != len(set(names)):
            raise ValueError("capability names must be unique")

    def capability(self, name: str) -> CapabilityManifest | None:
        return next((c for c in self.capabilities if c.name == name), None)

    def active_capabilities(self) -> tuple[CapabilityManifest, ...]:
        return tuple(c for c in self.capabilities if c.state is CapabilityState.ACTIVE)

    def with_candidate(self, capability: CapabilityManifest) -> "CognitiveBuild":
        if capability.state is not CapabilityState.CANDIDATE:
            raise ValueError("candidate manifest must have CANDIDATE state")
        if self.capability(capability.name) is not None:
            raise ValueError("capability already exists in build")
        return CognitiveBuild(self.build_id, self.software_version, self.capabilities + (capability,), self.parent_build)

    def promote(self, name: str) -> "CognitiveBuild":
        if self.capability(name) is None:
            raise ValueError("unknown capability")
        updated = tuple(
            CapabilityManifest(c.name, CapabilityState.ACTIVE if c.name == name else c.state, c.reliability, c.source_build)
            for c in self.capabilities
        )
        return CognitiveBuild(self.build_id, self.software_version, updated, self.parent_build)

    def hold(self, name: str) -> "CognitiveBuild":
        if self.capability(name) is None:
            raise ValueError("unknown capability")
        updated = tuple(
            CapabilityManifest(c.name, CapabilityState.HELD if c.name == name else c.state, c.reliability, c.source_build)
            for c in self.capabilities
        )
        return CognitiveBuild(self.build_id, self.software_version, updated, self.parent_build)
