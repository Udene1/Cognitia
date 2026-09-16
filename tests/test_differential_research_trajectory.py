from cognitia.adaptive_open_research import AdaptiveOpenResearch
from cognitia.environment import EnvironmentObservation
from cognitia.research_trajectory import reconstruct_trajectory
from cognitia.web_research import WebResearchBundle


QUESTION = "Why did service fail?"


class ScenarioWeb:
    def __init__(self, first_evidence: str):
        self.first_evidence = first_evidence
        self.calls: list[str] = []

    def investigate(self, question, *, limit, fetch_limit):
        self.calls.append(question)
        index = len(self.calls)
        content = self.first_evidence if index == 1 else (
            "Follow-up evidence was collected for the preceding research objective."
        )
        observation = EnvironmentObservation(
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
        return WebResearchBundle(QUESTION, (search,), (observation,))


def run_scenario(first_evidence: str):
    web = ScenarioWeb(first_evidence)
    episode = AdaptiveOpenResearch(web=web).investigate(
        QUESTION,
        max_rounds=2,
        search_results=1,
        documents_per_round=1,
        claims_per_document=5,
    )
    trajectory = reconstruct_trajectory(
        episode.result.question,
        episode.result.rounds,
        final_unresolved=episode.result.unresolved,
    )
    return web, episode, trajectory


def test_differential_first_evidence_changes_second_research_trajectory():
    resource_web, resource_episode, resource_trajectory = run_scenario(
        "Resource exhaustion caused the service failure."
    )
    dependency_web, dependency_episode, dependency_trajectory = run_scenario(
        "A dependency failure caused the service failure."
    )
    control_web, control_episode, control_trajectory = run_scenario(
        "Resource exhaustion caused the service failure."
    )

    assert resource_web.calls[0] == dependency_web.calls[0] == control_web.calls[0]
    assert resource_episode.result.rounds[0].documents[0].content != dependency_episode.result.rounds[0].documents[0].content

    resource_second = resource_episode.result.rounds[1]
    dependency_second = dependency_episode.result.rounds[1]
    control_second = control_episode.result.rounds[1]

    assert resource_second.parent_action_id == resource_episode.result.rounds[0].action_id
    assert dependency_second.parent_action_id == dependency_episode.result.rounds[0].action_id
    assert resource_second.information_need is not None
    assert dependency_second.information_need is not None
    assert resource_second.information_need_source_claim_ids
    assert dependency_second.information_need_source_claim_ids

    assert resource_second.action.query.objective != dependency_second.action.query.objective
    assert resource_second.information_need != dependency_second.information_need
    assert resource_second.information_need_source_claim_ids != dependency_second.information_need_source_claim_ids

    assert resource_second.action.query.objective == control_second.action.query.objective
    assert resource_second.information_need == control_second.information_need
    assert resource_trajectory.step(1).information_need == resource_second.information_need
    assert dependency_trajectory.step(1).information_need == dependency_second.information_need
    assert resource_trajectory.step(1).parent_action_id == resource_trajectory.step(0).action_id
    assert dependency_trajectory.step(1).parent_action_id == dependency_trajectory.step(0).action_id
