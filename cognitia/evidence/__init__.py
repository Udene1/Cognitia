"""Evidence acquisition, provenance, independence, and convergence primitives."""

from .model import Claim, EvidenceRecord, EvidenceSource, SourceLineage
from .graph import EvidenceGraph, EvidenceRelation
from .convergence import EvidenceConvergenceEngine, ConvergenceAssessment
from .model_checks import ModelConstraint, ModelConsistencyChecker, ModelCheckResult

__all__ = [
    "Claim", "EvidenceRecord", "EvidenceSource", "SourceLineage",
    "EvidenceGraph", "EvidenceRelation",
    "EvidenceConvergenceEngine", "ConvergenceAssessment",
    "ModelConstraint", "ModelConsistencyChecker", "ModelCheckResult",
]
