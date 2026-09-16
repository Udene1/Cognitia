from cognitia.adaptive_open_research import AdaptiveOpenResearch
from cognitia.environment import EnvironmentObservation
from cognitia.web_research import WebResearchBundle


class DifferentialWeb:
    def __init__(self, first_content: str):
        self.first_content = first_content
        self.calls: list[str] = []

    def investigate(self, question, *, limit, fetch_limit):
        self.calls.append(question)
        index = len(self.calls)
        content = self.first_content if index == 1 else "Independent evidence was retrieved for the preceding research target."
        document = EnvironmentObservation(
            id=f"document:{index}",
            source=f"source:{index}",
            content=content,
            reliability=0.7,
            metadata=(("kind", "web-document"), ("query", question)),
        )
        search = EnvironmentObservation(
            id=f"search:{index}",
            source=f"source:{index}",
            content=question,
            reliability=0.7,
            metadata=(("kind", "search_result"), ("query", question)),
        )
        return WebResearchBundle(question, (search,), (document,))


def _second_objective(first_content: str) -> str:
    web = DifferentialWeb(first_content)
    episode = AdaptiveOpenResearch(web=web).investigate(
        "Why did service fail?",
        max_rounds=2,
        search_results=1,
        documents_per_round=1,
        claims_per_document=20,
    )
    assert len(episode.result.rounds) == 2
    assert episode.information_needs
    return episode.result.rounds[1].action.query.objective


def test_different_first_round_evidence_changes_second_research_action():
    resource_exhaustion = _second_objective(
        "Resource exhaustion caused service failure. The evidence is uncertain because the observation was indirect."
    )
    dependency_failure = _second_objective(
        "The dependency failure caused service failure. The evidence is uncertain because the observation was indirect."
    )

    assert resource_exhaustion != dependency_failure
    assert "resource exhaustion" in resource_exhaustion.lower()
    assert "dependency failure" in dependency_failure.lower()
