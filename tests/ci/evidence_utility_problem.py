"""Real reasoning problem: candidate evidence must become a decision state."""
from cognitia.evidence.landscape import EvidenceLandscapeEngine, ResearchQuestion
from cognitia.evidence.model import Claim, EvidenceRecord, EvidenceSource, SourceLineage


def main() -> None:
    question = ResearchQuestion("q", "Did intervention A improve outcome?", ("a", "b"))
    claims = (
        Claim("a", "Intervention A improves outcome", "experiment"),
        Claim("b", "Intervention A does not improve outcome", "experiment"),
    )
    evidence = (
        EvidenceRecord(
            "e1", "a", EvidenceSource("lab-1", "experiment", "Independent lab", 0.85),
            "held-out trial improved outcome", True,
            SourceLineage("lab-1"), method="randomized trial",
        ),
        EvidenceRecord(
            "e2", "b", EvidenceSource("prod-1", "production", "Production telemetry", 0.90),
            "production cohort showed no improvement", True,
            SourceLineage("prod-1"), method="production observation",
        ),
    )
    decision = EvidenceLandscapeEngine().assess(question, claims, evidence)
    assert decision.conclusion == "conflicted"
    assert decision.confidence == 0.0
    assert decision.next_action.startswith("run a discriminating investigation")
    assert decision.unresolved_gaps
    print("EVIDENCE_UTILITY_PROBLEM_SUCCESS")
    print(f"CONCLUSION={decision.conclusion}")
    print(f"NEXT_ACTION={decision.next_action}")
    print(f"GAPS={len(decision.unresolved_gaps)}")


if __name__ == "__main__":
    main()
