from cognitia.evidence import (
    Claim, EvidenceConvergenceEngine, EvidenceRecord, EvidenceSource, SourceLineage,
    ModelConstraint, ModelConsistencyChecker,
)


def test_shared_upstream_sources_are_not_counted_as_independent():
    claim = Claim("c", "x", "domain")
    original = EvidenceSource("original", "paper", "Original", 0.9)
    copy = EvidenceSource("copy", "blog", "Copy", 0.8)
    independent = EvidenceSource("independent", "experiment", "Replication", 0.9)
    records = (
        EvidenceRecord("a", "c", original, "x", True, SourceLineage("original")),
        EvidenceRecord("b", "c", copy, "x", True, SourceLineage("copy", ("original",), "copied")),
        EvidenceRecord("d", "c", independent, "x", True, SourceLineage("independent")),
    )
    result = EvidenceConvergenceEngine().assess(claim, records)
    assert result.independent_support_groups == 2


def test_contradiction_is_not_erased_by_more_supporting_words():
    claim = Claim("c", "x", "domain")
    source = EvidenceSource("s", "experiment", "measurement", 0.9)
    records = (
        EvidenceRecord("a", "c", source, "supports", True),
        EvidenceRecord("b", "c", EvidenceSource("s2", "experiment", "replication", 0.95), "contradicts", False),
    )
    result = EvidenceConvergenceEngine().assess(claim, records)
    assert result.status == "contradicted"


def test_model_conflict_remains_a_model_check_result():
    constraint = ModelConstraint("m", "physics", "value near 10", lambda ctx: abs(ctx["value"] - 10) < 0.1)
    result = ModelConsistencyChecker().check(constraint, {"value": 12})
    assert result.passed is False
    assert result.reason == "model_conflict"
