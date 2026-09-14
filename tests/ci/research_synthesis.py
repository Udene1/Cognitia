from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.open_research import OpenResearchResult
from cognitia.research_synthesis import ResearchSynthesisEngine


def main() -> None:
    observations = (
        EnvironmentObservation(
            "doc:1", "web:history:a",
            "Political instability weakened the Roman Empire through repeated civil conflict.",
            metadata=(("origin_id", "origin:a"),),
        ),
        EnvironmentObservation(
            "doc:2", "web:history:b",
            "Frontier pressure contributed to the decline of the Roman Empire by weakening its armed forces.",
            metadata=(("origin_id", "origin:b"),),
        ),
        EnvironmentObservation(
            "doc:3", "web:history:c",
            "Fiscal strain contributed to the decline because tax revenue became less reliable.",
            metadata=(("origin_id", "origin:c"),),
        ),
    )
    extractor = DocumentClaimExtractor()
    claims = tuple(c for doc in observations for c in extractor.extract(doc))
    assert len(claims) == 3, claims

    genealogy = __import__("cognitia.evidence.genealogy", fromlist=["EvidenceGenealogyBuilder"]).EvidenceGenealogyBuilder()
    assessment = genealogy.assess(observations, claims)
    result = OpenResearchResult(
        question="Why did the Roman Empire decline?",
        rounds=(),
        claims=claims,
        clusters=(),
        unresolved=(),
        genealogy=assessment,
        stop_reason="test_fixture",
    )
    synthesis = ResearchSynthesisEngine().synthesize(result)

    assert synthesis.status == "candidate_multi_factor_synthesis"
    assert len(synthesis.factors) == 3
    assert len(synthesis.competing_explanations) >= 2
    assert len(synthesis.distinguishing_evidence) >= 2
    assert "multi-factor explanation" in synthesis.thesis
    assert "candidate" in synthesis.factors[0].confidence

    print("RESEARCH_SYNTHESIS_SUCCESS")
    print(f"STATUS={synthesis.status}")
    print(f"FACTORS={len(synthesis.factors)}")
    print(f"COMPETING_EXPLANATIONS={len(synthesis.competing_explanations)}")
    print(f"DISTINGUISHING_TESTS={len(synthesis.distinguishing_evidence)}")
    print(synthesis.render())


if __name__ == "__main__":
    main()
