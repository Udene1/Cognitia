from cognitia.adaptive_open_research import AdaptiveOpenResearch
from cognitia.environment import EnvironmentObservation
from cognitia.research_trajectory import reconstruct_trajectory
from cognitia.web_research import WebResearchBundle


QUESTION = "Why did service fail?"


class ScenarioWeb:
    def __init__(self, first_evidence: str):
        self.first_evidence = first_evidence
        self.calls = []

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


def test_differential_experiment_harness_preserves_controls():
    resource_web, resource_episode, resource_trajectory = run_scenario(
        "Resource exhaustion caused the service failure."
    )
    dependency_web, dependency_episode, dependency_trajectory = run_scenario(
        "A dependency failure caused the service failure."
    )
    control_web, control_episode, control_trajectory = run_scenario(
        "Resource exhaustion caused the service failure."
    )

    # Experimental integrity, not a predicted scientific outcome.
    assert resource_web.calls == dependency_web.calls == control_web.calls
    assert resource_episode.result.question == dependency_episode.result.question == QUESTION
    assert len(resource_episode.result.rounds) == len(dependency_episode.result.rounds) == len(control_episode.result.rounds) == 2

    first_resource = resource_episode.result.rounds[0]
    first_dependency = dependency_episode.result.rounds[0]
    first_control = control_episode.result.rounds[0]
    assert first_resource.action.query.objective == first_dependency.action.query.objective == first_control.action.query.objective
    assert first_resource.documents[0].content == first_control.documents[0].content
    assert first_resource.documents[0].content != first_dependency.documents[0].content

    # Every second step must remain linked to its own preceding action and
    # expose the evidence references that were actually available to the
    # controller. Whether the resulting trajectories diverge is observed by
    # the CI harness rather than asserted here.
    for episode, trajectory in (
        (resource_episode, resource_trajectory),
        (dependency_episode, dependency_trajectory),
        (control_episode, control_trajectory),
    ):
        first, second = episode.result.rounds
        assert second.parent_action_id == first.action_id
        assert second.information_need is not None
        assert second.information_need_source_claim_ids
        assert trajectory.step(1).parent_action_id == trajectory.step(0).action_id
        assert trajectory.step(1).information_need_source_claim_ids == second.information_need_source_claim_ids

    # The same-evidence control is a reproducibility check. If deterministic
    # execution changes this, that is a research observation rather than a
    # reason to hide the result behind a divergence assertion.
    resource_second = resource_episode.result.rounds[1]
    control_second = control_episode.result.rounds[1]
    assert resource_second.action.query.objective == control_second.action.query.objective
    assert resource_second.information_need == control_second.information_need
