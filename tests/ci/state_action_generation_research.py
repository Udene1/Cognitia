"""Experiment: remove planner-authored intermediate action vocabulary.

The evaluator supplies only a problem state and permitted operations. Cognitia
constructs candidate objectives from the state. No expected action string or
planner facet is supplied. The artifact records the generation trajectory so
later selection/observation experiments can consume the same boundary.
"""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState, EpistemicOutcome
from cognitia.state_action_generation import AvailableOperation, StateActionGenerator

OPERATIONS = (
    AvailableOperation("inspect", "inspect an available source"),
    AvailableOperation("compare", "compare independent observations"),
    AvailableOperation("reconstruct", "reconstruct the relevant sequence"),
)


TRAIN_STATE = CognitiveState(
    "Why did invoice processing stop after the primary database became unavailable?",
    evidence_ids=("db-outage",),
    hypothesis_ids=("dependency-failure", "recovery-order"),
    uncertainty=("cause",),
    goal="identify the cause without assuming a single explanation",
)

CONFLICT_STATE = CognitiveState(
    "Why did archival jobs cease following a storage-service interruption?",
    evidence_ids=("storage-outage", "restart-observation"),
    hypothesis_ids=("dependency-failure", "recovery-order"),
    uncertainty=("cause", "conflicting-observations"),
    goal="distinguish competing explanations",
)

PARTIAL_STATE = CognitiveState(
    "What caused archival jobs to resume after the storage-service interruption?",
    evidence_ids=("storage-outage",),
    hypothesis_ids=("recovery-order",),
    uncertainty=("cause",),
)


def record(label: str, state: CognitiveState) -> dict:
    actions = StateActionGenerator().generate(state, OPERATIONS, max_actions=8)
    return {
        "condition": label,
        "state": {
            "problem": state.problem,
            "evidence_ids": list(state.evidence_ids),
            "hypothesis_ids": list(state.hypothesis_ids),
            "uncertainty": list(state.uncertainty),
            "goal": state.goal,
        },
        "available_operations": [op.name for op in OPERATIONS],
        "generated_actions": [
            {
                "operation": action.operation.name,
                "objective": action.objective,
                "source_signals": list(action.source_signals),
                "rationale": action.rationale,
            }
            for action in actions
        ],
    }


def main() -> None:
    records = [
        record("training_state", TRAIN_STATE),
        record("changed_surface_and_conflict", CONFLICT_STATE),
        record("partial_state", PARTIAL_STATE),
    ]

    training = records[0]["generated_actions"]
    conflict = records[1]["generated_actions"]
    partial = records[2]["generated_actions"]
    objectives = {item["objective"] for item in training}

    artifact = {
        "experiment": "state-action-generation-v1",
        "research_question": "Can candidate intermediate actions be generated from current cognitive state rather than from researcher-authored search facets?",
        "records": records,
        "observations": {
            "generated_candidates_exist": bool(training),
            "changed_state_changes_generated_actions": {
                "conflict": {item["objective"] for item in conflict} != objectives,
                "partial": {item["objective"] for item in partial} != objectives,
            },
            "candidate_sources_are_state_signals": all(
                item["source_signals"] for item in training + conflict + partial
            ),
            "researcher_expected_action_supplied": False,
            "planner_authored_search_facets_used": False,
        },
        "boundary": "This experiment establishes only the behavior of the explicit state-to-action-generation mechanism under these inputs. It does not establish general cognition, learning, transfer, or usefulness in the world.",
        "next_step": "Feed these generated actions into an auditable selector, execute a real or controlled operation, record expected and observed consequences, and update the cognitive state without replacing the generated candidate set with evaluator-authored actions.",
    }
    output = Path(".ci/state-action-generation-research.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
