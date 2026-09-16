"""CI experiment for cross-question structural transfer of evidence-conditioned research.

The harness varies question wording and evidence content while keeping the
AdaptiveOpenResearch controller unchanged. It records the observed first
state and the selected second action. The experiment does not encode a
question -> action mapping.
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass

from cognitia.adaptive_open_research import AdaptiveOpenResearch
from cognitia.environment import EnvironmentObservation
from cognitia.research_trajectory import reconstruct_trajectory
from cognitia.web_research import WebResearchBundle


@dataclass(frozen=True)
class Scenario:
    name: str
    question: str
    evidence: tuple[str, ...]
    expected_structural_class: str


class ScenarioWeb:
    def __init__(self, evidence: tuple[str, ...]):
        self.evidence = evidence
        self.calls: list[str] = []

    def investigate(self, question, *, limit, fetch_limit):
        self.calls.append(question)
        round_number = len(self.calls)
        contents = self.evidence if round_number == 1 else (
            "Follow-up evidence was collected for the preceding research objective.",
        )
        documents = tuple(
            EnvironmentObservation(
                id=f"document:{round_number}:{index}",
                source=f"source:{round_number}:{index}",
                content=content,
                reliability=0.7,
                metadata=(("kind", "web-document"), ("query", question)),
            )
            for index, content in enumerate(contents)
        )
        search = EnvironmentObservation(
            id=f"search:{round_number}",
            source=f"source:{round_number}",
            content=question,
            reliability=0.7,
            metadata=(("kind", "search_result"), ("query", question)),
        )
        return WebResearchBundle(question, (search,), documents)


def run(scenario: Scenario) -> dict[str, object]:
    web = ScenarioWeb(scenario.evidence)
    episode = AdaptiveOpenResearch(web=web).investigate(
        scenario.question,
        max_rounds=2,
        search_results=1,
        documents_per_round=2,
        claims_per_document=5,
    )
    trajectory = reconstruct_trajectory(
        episode.result.question,
        episode.result.rounds,
        final_unresolved=episode.result.unresolved,
    )
    first, second = trajectory.steps
    first_round = episode.result.rounds[0]
    return {
        "name": scenario.name,
        "question": scenario.question,
        "expected_structural_class": scenario.expected_structural_class,
        "input_evidence": list(scenario.evidence),
        "calls": list(web.calls),
        "first_state": {
            "claim_count": len(first_round.claims),
            "claim_confidences": sorted(claim.confidence for claim in first_round.claims),
            "polarities": sorted(claim.polarity for claim in first_round.claims),
            "conflict": any(cluster.conflict for cluster in first_round.clusters),
        },
        "second_action": {
            "action_id": second.action_id,
            "purpose": second.purpose,
            "objective": second.objective,
            "information_need": second.information_need,
            "source_claim_ids": list(second.information_need_source_claim_ids),
            "source_document_ids": list(second.information_need_source_document_ids),
            "parent_action_id": second.parent_action_id,
            "decision_rationale": second.decision_rationale,
        },
        "trajectory": [
            {
                "sequence": step.sequence,
                "action_id": step.action_id,
                "purpose": step.purpose,
                "objective": step.objective,
                "information_need": step.information_need,
                "claim_ids": list(step.claim_ids),
                "document_ids": list(step.document_ids),
            }
            for step in trajectory.steps
        ],
    }


def main() -> None:
    # Each pair below has different surface wording but the same structural
    # evidence condition. No expected action/query is encoded in the scenario.
    scenarios = (
        Scenario("supported-a", "Why did the payment service stop?", ("The payment service stopped because its database was unavailable.",), "supported"),
        Scenario("supported-b", "What caused the archive worker to stop?", ("The archive worker stopped because its database was unavailable.",), "supported"),
        Scenario("conflict-a", "Why did the sensor gateway fail?", ("The sensor gateway failed because the network was unavailable.", "The sensor gateway did not fail because the network was unavailable."), "conflict"),
        Scenario("conflict-b", "Why did the billing gateway fail?", ("The billing gateway failed because the network was unavailable.", "The billing gateway did not fail because the network was unavailable."), "conflict"),
        Scenario("uncertain-a", "Why is the model output unstable?", ("The model output may be unstable because the input distribution changed.",), "uncertain"),
        Scenario("uncertain-b", "Why is the forecast changing?", ("The forecast may be changing because the input distribution changed.",), "uncertain"),
        Scenario("empty-a", "Why did the cache miss?", ("No usable causal statement was observed in the available material.",), "empty"),
        Scenario("empty-b", "Why did the queue stall?", ("The available material contained no usable causal statement.",), "empty"),
    )
    records = [run(scenario) for scenario in scenarios]

    # Integrity checks only: the controller is identical and every second
    # action is causally linked to its own first state. We do not assert which
    # concrete query the planner should produce.
    for record in records:
        assert len(record["calls"]) == 2
        assert record["second_action"]["parent_action_id"] == record["trajectory"][0]["action_id"]
        assert record["second_action"]["information_need"]

    by_class: dict[str, list[dict[str, object]]] = {}
    for record in records:
        by_class.setdefault(record["expected_structural_class"], []).append(record)

    # The discriminator is deliberately at the abstract action-purpose level:
    # equivalent structural states should preserve the controller's action
    # category across held-out questions, while different states should not be
    # silently collapsed into one category.
    same_class_consistency = {
        key: len({item["second_action"]["purpose"] for item in values}) == 1
        for key, values in by_class.items()
    }
    structural_purposes = {
        key: sorted({item["second_action"]["purpose"] for item in values})
        for key, values in by_class.items()
    }
    different_class_separation = len(set(tuple(value) for value in structural_purposes.values())) > 1

    observation = {
        "same_structural_class_same_action_purpose": same_class_consistency,
        "observed_action_purposes_by_class": structural_purposes,
        "different_classes_show_more_than_one_action_purpose": different_class_separation,
    }

    record = {
        "experiment": "structural-transfer-evidence-conditioned-research-v1",
        "research_question": "When surface questions change but evidence-state structure is held equivalent, does evidence-conditioned research behavior transfer without question-specific routing?",
        "hypothesis": "Structurally equivalent evidence states may produce the same abstract next-action category across held-out questions, while structurally different states may produce different categories.",
        "controller": "AdaptiveOpenResearch",
        "controls": {
            "same_controller": True,
            "rounds": 2,
            "search_results": 1,
            "documents_per_round": 2,
            "claims_per_document": 5,
            "question_specific_action_mapping": False,
        },
        "scenarios": records,
        "observation": observation,
        "interpretation_boundary": "This experiment can establish only whether the existing researcher-authored evidence-conditioned controller generalizes an action category across changed questions. Even consistent transfer is not learned cognition: the routing rules remain explicitly implemented. A later experiment must expose experience and test whether consequences alter future behavior on held-out problems.",
    }
    output = Path(".ci/structural-transfer-research.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
