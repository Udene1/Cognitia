"""CI exercise: correlated web sources must not masquerade as independent evidence."""
from cognitia.evidence import (
    Claim, EvidenceConvergenceEngine, EvidenceRecord, EvidenceSource, SourceLineage,
    ModelConstraint, ModelConsistencyChecker,
)

claim = Claim("claim:water", "water boils at 100 C at standard pressure", "physics")
original = EvidenceSource("source:experiment", "experiment", "independent measurement", 0.95)
copy = EvidenceSource("source:blog", "web", "blog copy", 0.30)
replication = EvidenceSource("source:replication", "experiment", "independent replication", 0.90)

evidence = (
    EvidenceRecord("e1", claim.id, original, "measured boiling point", True, SourceLineage(original.id)),
    EvidenceRecord("e2", claim.id, copy, "measured boiling point", True, SourceLineage(copy.id, (original.id,), "copied")),
    EvidenceRecord("e3", claim.id, replication, "independent measurement", True, SourceLineage(replication.id)),
)
assessment = EvidenceConvergenceEngine().assess(claim, evidence)
assert assessment.independent_support_groups == 2, assessment
assert assessment.status == "supported", assessment

constraint = ModelConstraint(
    "physics:boiling", "standard-atmosphere-model", "predicted boiling point is 100 C",
    lambda context: abs(float(context["observed_c"]) - 100.0) <= 0.5,
)
check = ModelConsistencyChecker().check(constraint, {"observed_c": 100.2})
assert check.passed is True
conflict = ModelConsistencyChecker().check(constraint, {"observed_c": 112.0})
assert conflict.passed is False

print("EVIDENCE_CONVERGENCE_SUCCESS")
