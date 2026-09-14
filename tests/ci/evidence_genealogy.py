"""Capability proof: many findings must not inflate independent evidence."""
from cognitia.document_claims import ExtractedClaim
from cognitia.environment import EnvironmentObservation
from cognitia.evidence.genealogy import EvidenceGenealogyBuilder


def claim(identifier: str, observation: str, text: str) -> ExtractedClaim:
    return ExtractedClaim(
        id=identifier,
        proposition=text,
        observation_id=observation,
        source="web",
        sentence=text,
        confidence="candidate",
    )


def main() -> None:
    observations = (
        EnvironmentObservation("doc:a", "web", "A report says the empire declined after repeated frontier pressure.", metadata=(("url", "https://example.test/a"),)),
        EnvironmentObservation("doc:b", "web", "Another article repeats the same frontier pressure finding.", metadata=(("url", "https://example.test/b"),)),
        EnvironmentObservation("doc:c", "web", "An independent archaeological record reports a different population trend.", metadata=(("url", "https://example.test/c"),)),
    )
    claims = (
        claim("c1", "doc:a", "The empire declined after repeated frontier pressure."),
        claim("c2", "doc:a", "Frontier pressure increased before the decline."),
        claim("c3", "doc:b", "The empire declined after repeated frontier pressure."),
        claim("c4", "doc:c", "Archaeological records show a different population trend."),
    )
    assessment = EvidenceGenealogyBuilder().assess(observations, claims)

    print("EVIDENCE_GENEALOGY")
    print(f"findings={assessment.finding_count}")
    print(f"observed_origins={assessment.observed_origin_count}")
    print(f"candidate_independent_origins={assessment.candidate_independent_origin_count}")
    print(f"derivative_links={assessment.derivative_links}")

    assert assessment.finding_count == 4
    assert assessment.observed_origin_count == 3
    assert assessment.candidate_independent_origin_count < assessment.finding_count
    assert assessment.candidate_independent_origin_count >= 1
    print("EVIDENCE_GENEALOGY_SUCCESS")


if __name__ == "__main__":
    main()
