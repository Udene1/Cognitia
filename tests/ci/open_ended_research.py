from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.open_research import OpenEndedResearch
from cognitia.research_search import ResearchSearchPlanner, SearchAction
from cognitia.web_research import WebResearchBundle


class RecordingWeb:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def investigate(self, question: str, *, limit: int, fetch_limit: int) -> WebResearchBundle:
        self.queries.append(question)
        suffix = "history" if "history" in question.lower() else "mechanism"
        observations = (
            EnvironmentObservation(
                id=f"search:{len(self.queries)}",
                source="web:test-search",
                content=f"Result for {question}",
                metadata=(("kind", "search_result"), ("query", question)),
            ),
        )
        documents = (
            EnvironmentObservation(
                id=f"document:{len(self.queries)}",
                source=f"web:test-document:{suffix}",
                content=(
                    "The system changed over time. "
                    "The mechanism is documented by independent observations. "
                    "Some reports may disagree with the historical account."
                ),
                metadata=(("kind", "web-document"), ("query", question)),
            ),
        )
        return WebResearchBundle(question, observations, documents)


def main() -> None:
    web = RecordingWeb()
    result = OpenEndedResearch(web=web).investigate(
        "Why did the system change and what is the history behind it?",
        max_rounds=3,
    )
    assert len(result.rounds) == 3
    assert len(web.queries) == 3
    assert result.claims
    assert all(claim.observation_id.startswith("document:") for claim in result.claims)
    assert result.status in {"conflicted", "candidate_evidence_landscape", "thin_evidence"}
    assert result.unresolved
    print("OPEN_ENDED_RESEARCH_SUCCESS")
    print(f"rounds={len(result.rounds)} claims={len(result.claims)} clusters={len(result.clusters)} status={result.status}")


if __name__ == "__main__":
    main()
