"""Capability-level proof for analogy as a testable search mechanism."""
from cognitia.learning.structural_transfer import StructuralPattern, StructuralTransferEngine


def main() -> None:
    engine = StructuralTransferEngine(
        (
            StructuralPattern(
                name="resource-allocation",
                features=("partition", "allocate", "constraint", "feedback", "objective"),
                source="engineering-artifact",
                confidence=0.9,
                epistemic_status="validated_pattern",
            ),
            StructuralPattern(
                name="simple-sequence",
                features=("sequence", "output"),
                source="text-artifact",
                confidence=0.8,
            ),
        )
    )

    # Vocabulary is intentionally unrelated to the source artifact. The
    # retrieval is driven by structural features only.
    candidates = engine.retrieve(
        ("partition", "allocate", "constraint", "feedback", "objective", "measurement"),
        minimum_similarity=0.4,
    )
    assert candidates
    candidate = candidates[0]
    assert candidate.pattern.name == "resource-allocation"
    assert candidate.similarity > 0.7
    assert candidate.status == "candidate"
    assert any("measurement" in item for item in candidate.adaptation)

    verified = engine.verify(
        candidate,
        (
            {"verified": True, "description": "target allocation reduced measured waste"},
            {"verified": True, "description": "independent target case reproduced the improvement"},
        ),
    )
    assert verified.passed
    assert "verified" in verified.reason

    falsified = engine.verify(
        candidate,
        ({"verified": True, "description": "first target case passed"}, {"verified": False, "description": "held-out case failed"}),
    )
    assert not falsified.passed

    unverified = engine.verify(candidate, ({"description": "anecdotal resemblance"},))
    assert not unverified.passed

    print("STRUCTURAL_TRANSFER_SUCCESS")
    print(f"candidate={candidate.pattern.name} similarity={candidate.similarity:.3f}")
    print(f"verification={verified.passed} falsified={falsified.passed} unverified={unverified.passed}")


if __name__ == "__main__":
    main()
