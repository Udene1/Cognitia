"""Run an actually open-ended Cognitia research experiment against the live web.

No answer is embedded here. The question is intentionally broad; CI records the
searches, why each action was chosen, retrieved documents, extracted claims,
conflicts, unresolved gaps, and the resulting candidate multi-factor synthesis.
"""
from cognitia.open_research import OpenEndedResearch
from cognitia.research_synthesis import ResearchSynthesisEngine


QUESTION = "Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?"


def main() -> None:
    result = OpenEndedResearch().investigate(
        QUESTION,
        max_rounds=4,
        search_results=5,
        documents_per_round=3,
        claims_per_document=12,
    )
    synthesis = ResearchSynthesisEngine().synthesize(result)

    print("OPEN_ENDED_LIVE_RESEARCH")
    print(f"question={result.question}")
    print(f"status={result.status}")
    print(f"stop_reason={result.stop_reason}")
    print(f"rounds={len(result.rounds)} claims={len(result.claims)} clusters={len(result.clusters)}")
    for index, research_round in enumerate(result.rounds, start=1):
        print(f"ROUND {index}: purpose={research_round.action.purpose} query={research_round.action.query.objective}")
        print(f"  rationale={research_round.decision_rationale}")
        print(f"  expected_information_gain={research_round.expected_information_gain}")
        print(f"  search_observations={len(research_round.search_observations)} documents={len(research_round.documents)} claims={len(research_round.claims)}")
        for cluster in research_round.clusters[:5]:
            print(f"  CLAIM: {cluster.representative.proposition}")
            print(f"    sources={len(cluster.source_ids)} conflict={cluster.conflict}")

    print("\nSYNTHESIS")
    print(f"status={synthesis.status}")
    print(f"factors={len(synthesis.factors)}")
    for factor in synthesis.factors:
        print(f"FACTOR: {factor.factor}")
        print(f"  contribution={factor.contribution}")
        print(f"  sources={factor.source_count} origins={factor.origin_count} confidence={factor.confidence}")
    print("THESIS")
    print(synthesis.thesis)
    print("DISTINGUISHING_EVIDENCE")
    for item in synthesis.distinguishing_evidence:
        print(f"- {item}")
    print("NEXT_ACTIONS")
    for item in synthesis.next_actions:
        print(f"- {item}")
    print("CAVEATS")
    for item in synthesis.caveats:
        print(f"- {item}")

    if not result.rounds:
        raise AssertionError("live research produced no rounds")
    if not any(round.search_observations for round in result.rounds):
        raise AssertionError("live research produced no search observations")
    if not any(round.decision_rationale for round in result.rounds):
        raise AssertionError("live research did not expose action-selection reasoning")
    print("LIVE_OPEN_ENDED_RESEARCH_SUCCESS")


if __name__ == "__main__":
    main()
