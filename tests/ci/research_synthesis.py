from cognitia.open_research import OpenEndedResearch
from cognitia.research_synthesis import ResearchSynthesisEngine


QUESTION = "Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?"


def main() -> None:
    # This benchmark intentionally contains no hand-authored political,
    # military, or economic factors. The evidence landscape must be acquired
    # and extracted by Cognitia itself.
    result = OpenEndedResearch().investigate(
        QUESTION,
        max_rounds=4,
        search_results=5,
        documents_per_round=3,
        claims_per_document=20,
    )
    synthesis = ResearchSynthesisEngine().synthesize(result)

    assert result.rounds, "no search actions were selected"
    assert result.claims, "no claims were acquired from the live evidence layer"
    assert synthesis.factors, "no explanatory factors were formed from acquired evidence"
    assert synthesis.status in {
        "candidate_multi_factor_synthesis",
        "thin_evidence_multi_factor_synthesis",
    }
    assert len(synthesis.distinguishing_evidence) >= 1
    assert "multiple potentially complementary contributing factors" in synthesis.thesis
    assert all("candidate" in factor.confidence for factor in synthesis.factors)

    print("RESEARCH_SYNTHESIS_SUCCESS")
    print(f"STATUS={synthesis.status}")
    print(f"SEARCH_ROUNDS={len(result.rounds)}")
    print(f"CLAIMS={len(result.claims)}")
    print(f"FACTORS={len(synthesis.factors)}")
    print(f"COMPLEMENTARY_DOMAINS={synthesis.complementary_domains}")
    print(f"COMPETING_EXPLANATIONS={len(synthesis.competing_explanations)}")
    print(f"DISTINGUISHING_TESTS={len(synthesis.distinguishing_evidence)}")
    print(synthesis.render())


if __name__ == "__main__":
    main()
