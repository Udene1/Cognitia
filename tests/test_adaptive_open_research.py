from cognitia.adaptive_open_research import AdaptiveOpenResearch
from cognitia.environment import EnvironmentObservation
from cognitia.research_trajectory import reconstruct_trajectory
from cognitia.web_research import WebResearchBundle


class FakeWeb:
    def __init__(self):
        self.calls = []

    def investigate(self, question, *, limit, fetch_limit):
        self.calls.append(question)
        index = len(self.calls)
        if index == 1:
            content = "Resource exhaustion caused service failure. The evidence is uncertain because the observation was indirect."
        else:
            content = "Independent evidence was reported for resource exhaustion. The failure was not caused by the dependency."
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
        return WebResearchBundle(question, (search,), (observation,))


def test_second_research_action_is_derived_from_first_round_evidence():
    web = FakeWeb()
    episode = AdaptiveOpenResearch(web=web).investigate(
        "Why did service A fail?",
        max_rounds=2,
        search_results=1,
        documents_per_round=1,
        claims_per_document=5,
    )

    assert len(web.calls) == 2
    assert len(episode.result.rounds) == 2
    first = episode.result.rounds[0]
    second = episode.result.rounds[1]
    assert first.claims
    assert second.parent_action_id == first.action_id
    assert second.information_need is not None
    assert second.information_need_source_claim_ids
    source_claim = first.claims[0]
    assert source_claim.id in second.information_need_source_claim_ids
    assert source_claim.proposition in second.information_need
    assert second.action.query.objective != first.action.query.objective
    assert "preceding evidence" in second.decision_rationale or "source_claims" in second.decision_rationale

    trajectory = reconstruct_trajectory(
        episode.result.question,
        episode.result.rounds,
        final_unresolved=episode.result.unresolved,
    )
    assert trajectory.adaptive_transition_count == 1
    assert trajectory.step(1).parent_action_id == trajectory.step(0).action_id
    assert trajectory.step(1).information_need_source_claim_ids == second.information_need_source_claim_ids
