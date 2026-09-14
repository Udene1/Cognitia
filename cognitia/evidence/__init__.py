"""Evidence acquisition, provenance, independence, and convergence primitives."""

from .model import Claim, EvidenceRecord, EvidenceSource, SourceLineage
from .graph import EvidenceGraph, EvidenceRelation
from .convergence import EvidenceConvergenceEngine, ConvergenceAssessment
from .model_checks import ModelConstraint, ModelConsistencyChecker, ModelCheckResult
from .genealogy import EvidenceGenealogyBuilder, EvidenceOrigin, GenealogyAssessment
from .claim_identity import ClaimIdentity, ClaimIdentityMatcher

__all__ = [
    "Claim", "EvidenceRecord", "EvidenceSource", "SourceLineage",
    "EvidenceGraph", "EvidenceRelation",
    "EvidenceConvergenceEngine", "ConvergenceAssessment",
    "ModelConstraint", "ModelConsistencyChecker", "ModelCheckResult",
    "EvidenceGenealogyBuilder", "EvidenceOrigin", "GenealogyAssessment",
    "ClaimIdentity", "ClaimIdentityMatcher",
]
