"""CI execution harness for the differential research trajectory experiment."""
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
        "resource-exhaustion",
        "Resource exhaustion caused the service failure.",
    )
    dependency = run_scenario(
        "dependency-failure",
        "A dependency failure caused the service failure.",
    )
    control = run_scenario(
        "resource-control",
        "Resource exhaustion caused the service failure.",
    )

    assert resource["calls"][0] == dependency["calls"][0] == control["calls"][0]
    resource_second = resource["rounds"][1]
    dependency_second = dependency["rounds"][1]
    control_second = control["rounds"][1]

    assert resource_second["parent_action_id"] == resource["rounds"][0]["action_id"]
    assert dependency_second["parent_action_id"] == dependency["rounds"][0]["action_id"]
    assert resource_second["information_need"]
    assert dependency_second["information_need"]
    assert resource_second["information_need_source_claim_ids"]
    assert dependency_second["information_need_source_claim_ids"]

    # Differential observation: only the first evidence differs, but the next
    # information need and research objective differ as well.
    assert resource["first_evidence"] != dependency["first_evidence"]
    assert resource_second["information_need"] != dependency_second["information_need"]
    assert resource_second["objective"] != dependency_second["objective"]
    assert resource_second["information_need_source_claim_ids"] != dependency_second["information_need_source_claim_ids"]

    # Same-evidence control: repeating A must reproduce A's next action.
    assert resource_second["information_need"] == control_second["information_need"]
    assert resource_second["objective"] == control_second["objective"]

    record = {
        "experiment": "differential-research-trajectory-v1",
        "hypothesis": "Holding the question constant while changing only the first evidence will change the next information need and research objective when the preceding evidence changes.",
        "question": QUESTION,
        "observations": {
            "resource_exhaustion": resource,
            "dependency_failure": dependency,
            "resource_control": control,
        },
        "discriminator": {
            "same_question_initial_action": True,
            "different_first_evidence": True,
            "different_second_information_need": resource_second["information_need"] != dependency_second["information_need"],
            "different_second_objective": resource_second["objective"] != dependency_second["objective"],
            "same_evidence_control_reproduces_action": resource_second["objective"] == control_second["objective"],
        },
        "interpretation_boundary": "This demonstrates evidence-conditioned trajectory divergence in the implemented adaptive controller. It does not by itself demonstrate learned cognition; the next discriminator must test whether the behavior survives changed questions/states without researcher-authored routing rules.",
    }
    output = Path(".ci/differential-trajectory.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
