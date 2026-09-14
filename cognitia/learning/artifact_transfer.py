"""Build structural-transfer candidates from learned Cognitia artifacts.

This module deliberately does not decide that an analogy is valid. It bridges
existing learned representations into the structural-transfer engine so that
retrieval can become a normal research action rather than a manually supplied
list of patterns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .code_representation import ComputationalRepresentation
from .structural_transfer import StructuralPattern, StructuralTransferEngine, TransferCandidate


@dataclass(frozen=True)
class ArtifactStructure:
    """A domain-neutral structure recovered from a learned artifact."""

    artifact_id: str
    features: tuple[str, ...]
    source_kind: str
    epistemic_status: str
    confidence: float


def from_computation(artifact_id: str, representation: ComputationalRepresentation) -> ArtifactStructure:
    """Convert executable-code structure into a reusable structural signature."""
    features = tuple(dict.fromkeys((
        *representation.operations,
        *representation.control_flow,
        *representation.data_flow,
        "algorithm:" + representation.algorithm_family,
    )))
    return ArtifactStructure(
        artifact_id=artifact_id,
        features=features,
        source_kind="executable_code",
        epistemic_status=representation.epistemic_status,
        confidence=representation.confidence,
    )


def pattern_from_artifact(artifact: ArtifactStructure) -> StructuralPattern:
    return StructuralPattern(
        name=artifact.artifact_id,
        features=artifact.features,
        source=artifact.source_kind,
        epistemic_status=artifact.epistemic_status,
        confidence=artifact.confidence,
    )


class LearnedArtifactTransfer:
    """Retrieve candidate transfers from accumulated artifact structures."""

    def __init__(self, artifacts: Sequence[ArtifactStructure] = ()) -> None:
        self._engine = StructuralTransferEngine(pattern_from_artifact(item) for item in artifacts)

    def add(self, artifact: ArtifactStructure) -> None:
        self._engine.register(pattern_from_artifact(artifact))

    def retrieve(self, target_features: Iterable[str], *, minimum_similarity: float = 0.35, limit: int = 5) -> tuple[TransferCandidate, ...]:
        return self._engine.retrieve(tuple(target_features), minimum_similarity=minimum_similarity, limit=limit)
