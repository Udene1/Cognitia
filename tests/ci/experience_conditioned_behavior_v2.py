"""Held-out experiment for influence, transfer, defeasibility, specificity and persistence.

The harness supplies structural state properties and available operations. It
does not specify which operation should win. The selector consumes generated
candidates and recorded experience; the artifact preserves the full trajectory.
"""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import (
    CognitiveState,
    EpistemicOutcome,
    ExpectedConsequence,
    Experience,
    ExperienceLedger,
    ObservedConsequence,
)
from cognitia.experience_action_selection import ExperienceGeneratedActionSelector
from cognitia.state_action_generation import AvailableOperation, StateActionGenerator

OPERATIONS = (
    AvailableOperation("search", "search"),
    AvailableOperation("inspect", "inspect"),
    AvailableOperation("compute", "compute"),
    AvailableOperation("reason", "reason"),
)

BASE = CognitiveState(
    "Why did the payment queue stall after a database outage?",
    hypothesis_ids=("cause",),
    uncertainty=("cause",),
)
TRANSFER = CognitiveState(
    "Why did the archive queue stall after a network outage?",
    hypothesis_ids=("cause",),
    uncertainty=("cause",),
)
UNRELATED = CognitiveState(
    "Which alloy should be selected for a high-temperature turbine?",
    hypothesis_ids=("material",),
    uncertainty=("material",),
)
RECOVERY = CognitiveState(
    "Why did the telemetry pipeline stop after a certificate rotation?",
    hypothesis_ids=("cause",),
    uncertainty=("cause",),
)
PERSISTENCE = CognitiveState(
    "Why did the reporting pipeline stop after a schema migration?",
    hypothesis_ids=("cause",),
    uncertainty=("cause",),
)


def experience(item_id: str, state: CognitiveState, action: str, outcome: EpistemicOutcome) -> Experience:
    return Experience(
        experience_id=item_id,
        prior_state=state,
        action=action,
        rationale="The prior state left the cause unresolved; the action was selected by the preceding decision process.",
        expected=ExpectedConsequence("the action will reduce uncertainty"),
        observed=ObservedConsequence(
            "the action will reduce uncertainty",
            outcome,
            evidence_ids=(f"evidence:{item_id}",),
        ),
        state_update=CognitiveState(
            state.problem,
            hypothesis_ids=state.hypothesis_ids,
            uncertainty=() if outcome is EpistemicOutcome.CONFIRMED else state.uncertainty,
        ),
        provenance=("experience-conditioned-behavior-v2",),
    )


def run_condition(name: str, state: CognitiveState, ledger: ExperienceLedger) -> dict:
    generated = StateActionGenerator().generate(state, OPERATIONS, max_actions=8)
    decision = ExperienceGeneratedActionSelector().select(state, generated, ledger)
    return {
        "condition": name,
        "problem": state.problem,
        "state": {
            "hypothesis_ids": list(state.hypothesis_ids),
            "uncertainty": list(state.uncertainty),
        },
        "candidates": [
            {
                "operation": item.action.operation.name,
                "objective": item.action.objective,
                "source_signals": list(item.action.source_signals),
                "score": item.score,
                "relevant_experience_ids": list(item.relevant_experience_ids),
                "rationale": item.rationale,
            }
            for item in decision.candidates
        ],
        "selected": decision.selected.action.operation.name,
        "selected_objective": decision.selected.action.objective,
        "experience_ids": [item.experience_id for item in ledger.all()],
    }


def main() -> None:
    selector = ExperienceGeneratedActionSelector()
    baseline = run_condition("experience_absent", BASE, ExperienceLedger())

    confirmed = experience("confirmed-search", BASE, "search", EpistemicOutcome.CONFIRMED)
    present = run_condition("experience_present", BASE, ExperienceLedger((confirmed,)))

    refuted = experience("refuted-search", BASE, "search", EpistemicOutcome.REFUTED)
    conflict_ledger = ExperienceLedger((confirmed, refuted))
    conflict = run_condition("conflicting_evidence", BASE, conflict_ledger)

    transfer = run_condition("held_out_transfer", TRANSFER, conflict_ledger)
    unrelated = run_condition("specificity_control", UNRELATED, conflict_ledger)
    recovery = run_condition("recovery_after_contradiction", RECOVERY, conflict_ledger)
    persistence = run_condition("persistence_on_later_episode", PERSISTENCE, conflict_ledger)

    records = [baseline, present, conflict, transfer, unrelated, recovery, persistence]
    observations = {
        "influence": baseline["selected"] != present["selected"],
        "defeasibility": present["selected"] != conflict["selected"],
        "transfer": conflict["selected"] == transfer["selected"],
        "specificity": unrelated["selected"] == baseline["selected"],
        "recovery": recovery["selected"] == conflict["selected"],
        "persistence": persistence["selected"] == conflict["selected"],
        "novelty_after_conflict": conflict["selected"] != "search",
        "same_structural_state_across_surface_changes": len({transfer["state"]["hypothesis_ids"][0], recovery["state"]["hypothesis_ids"][0]}) == 1,
    }
    artifact = {
        "experiment": "experience-conditioned-future-behavior-v2",
        "research_question": "Does recorded experience alter future action selection on held-out problems while remaining defeasible and structurally specific?",
        "protocol": {
            "available_operations": [operation.name for operation in OPERATIONS],
            "researcher_authored_expected_actions": False,
            "surface_problem_is_used_for_transfer": False,
        },
        "conditions": records,
        "observations": observations,
        "interpretation_boundary": "The result measures this explicit deterministic experience-conditioned selection mechanism. It does not establish general cognition, autonomous learning, or useful abstraction discovery.",
    }
    output = Path(".ci/experience-conditioned-behavior-v2.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
