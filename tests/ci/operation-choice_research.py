"""Research experiment: search competes with non-search operations.

The purpose is not to prove semantic routing. It is to expose a measurable
choice boundary: several operations are available, each has an explicit cost,
and the selector must record why one is preferred from the current state.
"""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState
from cognitia.information_need import InformationNeedDetector
from cognitia.operation_selection import OperationOption, OperationSelector
from cognitia.state_action_generation import AvailableOperation

OPTIONS = (
    OperationOption(AvailableOperation("search", "use external evidence"), cost=0.40),
    OperationOption(AvailableOperation("inspect", "inspect local evidence"), cost=0.20),
    OperationOption(AvailableOperation("compute", "compute a result"), cost=0.10),
    OperationOption(AvailableOperation("reason", "reason over existing evidence"), cost=0.05),
)

STATES = (
    ("freshness", CognitiveState("What is the latest inflation rate?")),
    ("computation", CognitiveState("Calculate 17 * 23.")),
    ("sufficient_state", CognitiveState(
        "What follows from these observations?", evidence_ids=("e1", "e2")
    )),
    ("unresolved", CognitiveState("Why did this process fail?", uncertainty=("cause",))),
)


def main() -> None:
    detector = InformationNeedDetector()
    selector = OperationSelector()
    records = []
    for label, state in STATES:
        need = detector.detect(state)
        choice = selector.assess(state, need, OPTIONS)
        records.append({
            "condition": label,
            "problem": state.problem,
            "information_need": {
                "kind": need.kind.value,
                "reasons": list(need.reasons),
                "confidence": need.confidence,
            },
            "assessments": [
                {
                    "operation": item.operation.name,
                    "capability": item.operation.capability,
                    "expected_state_improvement": item.expected_state_improvement,
                    "cost": item.cost,
                    "risk": item.risk,
                    "net_value": item.net_value,
                    "reasons": list(item.reasons),
                }
                for item in choice.assessments
            ],
            "selected": choice.selected.operation.name if choice.selected else None,
        })

    artifact = {
        "experiment": "operation-choice-v1",
        "research_question": "Can external search be treated as one operation whose use depends on the current state rather than a default response?",
        "records": records,
        "observations": {
            "freshness_selected_external_search": records[0]["selected"] == "search",
            "computation_selected_without_search": records[1]["selected"] != "search",
            "sufficient_state_selected_without_search": records[2]["selected"] != "search",
            "all_conditions_recorded_competing_options": all(len(r["assessments"]) == len(OPTIONS) for r in records),
        },
        "boundary": "The information-need detector and operation selector are explicit deterministic hypotheses. They do not establish semantic understanding, general routing, learning, or the ability to decide correctly for arbitrary requests.",
        "next_step": "Execute the selected operation and record expected versus observed state change, acquisition cost, and whether the observation should revise future operation choice. Keep search and non-search operations under the same consequence ledger.",
    }
    output = Path(".ci/operation-choice-research.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
