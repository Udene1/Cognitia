"""Capability proof: learned executable structure becomes a transfer candidate."""
from cognitia.learning.artifact_transfer import LearnedArtifactTransfer, from_computation
from cognitia.learning.code_representation import PythonCodeInterpreter


def main() -> None:
    source = """
def totals(records):
    out = {}
    for record in records:
        key = record['group']
        out[key] = out.get(key, 0) + record['value']
    return out
"""
    representation = PythonCodeInterpreter().interpret(source)
    artifact = from_computation("grouped-total-solution", representation)
    learner = LearnedArtifactTransfer((artifact,))

    target = (
        "iterate records",
        "maintain keyed accumulator",
        "initialize missing key",
        "partition records by key",
        "combine values within each key",
        "emit one result per key",
    )
    candidates = learner.retrieve(target, minimum_similarity=0.45)
    assert candidates
    candidate = candidates[0]
    assert candidate.pattern.name == "grouped-total-solution"
    assert candidate.similarity >= 0.45

    verified = learner._engine.verify(candidate, ({"verified": True, "description": "held-out target matched grouped reduction"},))
    assert verified.passed

    falsified = learner._engine.verify(candidate, ({"verified": False, "description": "held-out target violated the adapted reduction"},))
    assert not falsified.passed

    unverified = learner._engine.verify(candidate, ({"description": "target observation without verdict"},))
    assert not unverified.passed
    assert "no explicit verification verdict" in unverified.reason

    print("ARTIFACT_STRUCTURAL_TRANSFER_SUCCESS")
    print(f"algorithm={representation.algorithm_family} similarity={candidate.similarity:.3f}")
    print(f"verified={verified.reason}")
    print(f"falsified={falsified.reason}")


if __name__ == "__main__":
    main()
