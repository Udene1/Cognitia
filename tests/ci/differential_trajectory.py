"""CI execution harness for the differential research trajectory experiment.

The harness is intentionally outcome-neutral. It controls the perturbation,
records the resulting trajectories, and lets the observation determine whether
the subsequent research path changed.
"""
from __future__ import annotations

import json
from pathlib import Path

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
        return WebResearchBundle(QUESTION, (search,), (document,))


def run_scenario(name: str, first_evidence: str):
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
    return {
        "name": name,
        "question": QUESTION,
        "calls": list(web.calls),
        "first_evidence": first_evidence,
        "rounds": [
            {
                "sequence": step.sequence,
                "action_id": step.action_id,
                "parent_action_id": step.parent_action_id,
                "objective": step.objective,
                "information_need": step.information_need,
                "information_need_source_claim_ids": list(step.information_need_source_claim_ids),
                "information_need_source_document_ids": list(step.information_need_source_document_ids),
                "decision_rationale": step.decision_rationale,
                "claim_ids": list(step.claim_ids),
                "document_ids": list(step.document_ids),
            }
            for step in trajectory.steps
        ],
    }


def main() -> None:
    resource = run_scenario(
        "condition-a",
        "Resource exhaustion caused the service failure.",
    )
    dependency = run_scenario(
        "condition-b",
        "A dependency failure caused the service failure.",
    )
    control = run_scenario(
        "same-evidence-control",
        "Resource exhaustion caused the service failure.",
    )

    # Harness integrity: the first search/action is held constant. We do not
    # require the full call sequence to remain equal because a changed second
    # query is itself one of the observations this experiment is measuring.
    assert resource["calls"][0] == dependency["calls"][0] == control["calls"][0]
    assert resource["question"] == dependency["question"] == control["question"] == QUESTION
    assert resource["first_evidence"] == control["first_evidence"]
    assert resource["first_evidence"] != dependency["first_evidence"]

    for scenario in (resource, dependency, control):
        assert len(scenario["rounds"]) == 2
        first, second = scenario["rounds"]
        assert second["parent_action_id"] == first["action_id"]
        assert second["information_need"]
        assert second["information_need_source_claim_ids"]
        assert second["information_need_source_document_ids"]

    resource_second = resource["rounds"][1]
    dependency_second = dependency["rounds"][1]
    control_second = control["rounds"][1]

    # Scientific outcome is observed, not prescribed. Both equality and
    # divergence are valid observations. The control tests reproducibility.
    observation = {
        "same_initial_question_and_action": resource["rounds"][0]["objective"]
        == dependency["rounds"][0]["objective"]
        == control["rounds"][0]["objective"],
        "first_evidence_changed": resource["first_evidence"] != dependency["first_evidence"],
        "second_search_query_changed": resource["calls"][1] != dependency["calls"][1],
        "second_information_need_changed": resource_second["information_need"]
        != dependency_second["information_need"],
        "second_objective_changed": resource_second["objective"] != dependency_second["objective"],
        "second_source_claims_changed": resource_second["information_need_source_claim_ids"]
        != dependency_second["information_need_source_claim_ids"],
        "same_evidence_control_reproduced_information_need": resource_second["information_need"]
        == control_second["information_need"],
        "same_evidence_control_reproduced_objective": resource_second["objective"]
        == control_second["objective"],
        "same_evidence_control_reproduced_second_search_query": resource["calls"][1]
        == control["calls"][1],
    }

    record = {
        "experiment": "differential-research-trajectory-v2",
        "research_question": "When the research question is held constant but the first acquired evidence differs, does the subsequent research trajectory change?",
        "hypothesis": "A change in the evidence state may change the subsequent research trajectory. The direction and magnitude of any change are not specified in advance.",
        "controls": {
            "question": QUESTION,
            "controller": "AdaptiveOpenResearch",
            "rounds": 2,
            "search_results": 1,
            "documents_per_round": 1,
            "claims_per_document": 5,
            "same_evidence_control": True,
        },
        "observations": {
            "condition_a": resource,
            "condition_b": dependency,
            "same_evidence_control": control,
        },
        "observation_summary": observation,
        "interpretation_boundary": "This experiment can establish only what the controlled trajectories show about the implemented controller. Divergence is evidence that the implemented controller is sensitive to the changed evidence state; equality is evidence that this perturbation did not change the subsequent trajectory. Neither result establishes learned cognition. The controller contains researcher-authored deterministic routing rules, so a later generalization experiment is required.",
    }
    output = Path(".ci/differential-trajectory.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
