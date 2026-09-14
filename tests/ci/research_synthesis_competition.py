from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.open_research import OpenResearchResult
from cognitia.research_synthesis import ResearchSynthesisEngine
from cognitia.evidence.genealogy import EvidenceGenealogyBuilder


def main() -> None:
    observations = (
        EnvironmentObservation(
            "doc:positive", "web:history:a",
            "Fiscal strain contributed to the decline of the Roman Empire.",
            metadata=(("origin_id", "origin:a"),),
        ),
        EnvironmentObservation(
            "doc:negative", "web:history:b",
            "Fiscal strain did not contribute to the decline of the Roman Empire.",
            metadata=(("origin_id", "origin:b"),),
        ),
    )
    extractor = DocumentClaimExtractor()
    claims = tuple(c for doc in observations for c in extractor.extract(doc))
    assert len(claims) == 2, claims
    assessment = EvidenceGenealogyBuilder().assess(observations, claims)
    result = OpenResearchResult(
        question="Did fiscal strain contribute to the decline of the Roman Empire?",
        rounds=(),
        claims=claims,
        clusters=(),
        unresolved=(),
        genealogy=assessment,
        stop_reason="competition_fixture",
    )
    synthesis = ResearchSynthesisEngine().synthesize(result)
    assert len(synthesis.factors) == 1
    assert len(synthesis.competing_explanations) == 1
    assert synthesis.distinguishing_evidence
    assert "contrary propositions" in synthesis.next_actions[2]
    print("RESEARCH_SYNTHESIS_COMPETITION_SUCCESS")
    print(f"FACTORS={len(synthesis.factors)}")
    print(f"COMPETING_EXPLANATIONS={len(synthesis.competing_explanations)}")
    print(f"DISTINGUISHING_TESTS={len(synthesis.distinguishing_evidence)}")
    print(synthesis.render())


if __name__ == "__main__":
    main()
