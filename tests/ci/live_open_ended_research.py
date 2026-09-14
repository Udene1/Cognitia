"""Run an actually open-ended Cognitia research experiment against the live web.

No answer is embedded here. The question is intentionally broad; CI records the
searches, retrieved documents, extracted claims, conflicts, and unresolved gaps.
"""
from cognitia.open_research import OpenEndedResearch


QUESTION = "Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?"


def main() -> None:
    result = OpenEndedResearch().investigate(
        QUESTION,
        max_rounds=4,
        search_results=5,
        documents_per_round=3,
        claims_per_document=12,
    )

    print("OPEN_ENDED_LIVE_RESEARCH")
    print(f"question={result.question}")
    print(f"status={result.status}")
    print(f"rounds={len(result.rounds)} claims={len(result.claims)} clusters={len(result.clusters)}")
    for index, research_round in enumerate(result.rounds, start=1):
        print(f"ROUND {index}: purpose={research_round.action.purpose} query={research_round.action.query.objective}")
        print(f"  search_observations={len(research_round.search_observations)} documents={len(research_round.documents)} claims={len(research_round.claims)}")
        for cluster in research_round.clusters[:5]:
            print(f"  CLAIM: {cluster.representative.proposition}")
            print(f"    sources={len(cluster.source_ids)} conflict={cluster.conflict}")
    print("UNRESOLVED")
    for gap in result.unresolved:
        print(f"- {gap}")

    if not result.rounds:
        raise AssertionError("live research produced no rounds")
    if not any(round.search_observations for round in result.rounds):
        raise AssertionError("live research produced no search observations")
    print("LIVE_OPEN_ENDED_RESEARCH_SUCCESS")


if __name__ == "__main__":
    main()
