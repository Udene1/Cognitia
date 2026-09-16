from cognitia.research_trajectory import reconstruct_trajectory


def test_empty_research_episode_is_recorded_without_invented_information():
    trajectory = reconstruct_trajectory(
        "Why did the Roman Empire decline?",
        (),
        final_unresolved=("Independent evidence remains thin.",),
    )

    assert trajectory.question == "Why did the Roman Empire decline?"
    assert trajectory.action_count == 0
    assert trajectory.observed_document_count == 0
    assert trajectory.observed_claim_count == 0
    assert trajectory.final_unresolved_information_needs == ("Independent evidence remains thin.",)


def test_trajectory_step_count_matches_executed_rounds():
    class ActionQuery:
        objective = "roman empire decline"

    class Action:
        query = ActionQuery()
        purpose = "direct evidence"
        priority = 1.0

    class Observation:
        id = "search:1"

    class Document:
        id = "document:1"
        source = "wikipedia"

    class Claim:
        id = "claim:1"

    class Cluster:
        conflict = False

    class ResearchRound:
        action = Action()
        search_observations = (Observation(),)
        documents = (Document(),)
        claims = (Claim(),)
        clusters = (Cluster(),)
        decision_rationale = "selected for direct evidence (priority=1.00)"
        expected_information_gain = 1.0

    trajectory = reconstruct_trajectory("roman empire decline", (ResearchRound(),))

    assert trajectory.action_count == 1
    assert trajectory.observed_document_count == 1
    assert trajectory.observed_claim_count == 1
    assert trajectory.step(0).search_observation_ids == ("search:1",)
    assert trajectory.step(0).document_ids == ("document:1",)
    assert trajectory.step(0).claim_ids == ("claim:1",)
    assert trajectory.step(0).unresolved_information_needs == ()
