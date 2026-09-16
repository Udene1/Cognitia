"""Full-loop experiment: experience -> abstraction -> action -> consequence -> future action."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ExperienceLedger, ObservedConsequence
from cognitia.experience_abstraction_decision import AbstractionConditionedActionSelector
from cognitia.state_action_generation import AvailableOperation

OPERATIONS = (
    AvailableOperation("search", "search"),
    AvailableOperation("inspect", "inspect"),
    AvailableOperation("compute", "compute"),
    AvailableOperation("reason", "reason"),
)


def make(item_id: str, problem: str, action: str, outcome: EpistemicOutcome) -> Experience:
    state = CognitiveState(problem)
    return Experience(
        experience_id=item_id,
        prior_state=state,
        action=action,
        rationale="selected by the preceding decision process",
        expected=ExpectedConsequence("the action will reduce uncertainty"),
        observed=ObservedConsequence("the action will reduce uncertainty", outcome, evidence_ids=(f"evidence:{item_id}",)),
        state_update=state,
        provenance=("experience-abstraction-consequence-loop",),
    )


def decision(label: str, problem: str, ledger: ExperienceLedger) -> dict:
    result = AbstractionConditionedActionSelector().select(problem, OPERATIONS, ledger)
    return {
        "label": label,
        "problem": problem,
        "selected": result.selected.action.operation.name,
        "selected_score": result.selected.score,
        "abstraction": list(result.abstraction),
        "candidates": [
            {
                "operation": item.action.operation.name,
                "score": item.score,
                "supporting_experience_ids": list(item.supporting_experience_ids),
                "rationale": item.rationale,
            }
            for item in result.candidates
        ],
    }


def main() -> None:
    seed_problem = "The database outage caused the payment queue to stall."
    held_out_problem = "The network outage caused the archive queue to stall."
    future_problem = "The certificate rotation caused the telemetry queue to stop."
    unrelated_problem = "Which alloy is suitable for a high-temperature turbine?"

    baseline = decision("no_experience", held_out_problem, ExperienceLedger())
    seed = make("confirmed-seed", seed_problem, "search", EpistemicOutcome.CONFIRMED)
    after_seed = decision("after_confirmed_experience", held_out_problem, ExperienceLedger((seed,)))

    consequence = make("contradicted-held-out", held_out_problem, "search", EpistemicOutcome.REFUTED)
    revised_ledger = ExperienceLedger((seed, consequence))
    after_consequence = decision("after_observed_contradiction", future_problem, revised_ledger)
    unrelated = decision("specificity_control", unrelated_problem, revised_ledger)

    artifact = {
        "experiment": "experience-abstraction-consequence-loop-v1",
        "research_question": "Can an induced abstraction participate in future action selection, then be revised by an observed consequence and affect a later linguistically novel action decision?",
        "protocol": {
            "researcher_supplied_structural_ids": False,
            "researcher_supplied_expected_action": False,
            "available_operations": [operation.name for operation in OPERATIONS],
        },
        "trajectory": [baseline, after_seed, after_consequence, unrelated],
        "observations": {
            "experience_changes_future_action": baseline["selected"] != after_seed["selected"],
            "contradicted_consequence_changes_future_action": after_seed["selected"] != after_consequence["selected"],
            "held_out_future_surface_differs": after_consequence["problem"] != after_seed["problem"],
            "specificity_control_unchanged": unrelated["selected"] == baseline["selected"],
            "full_loop_executed": True,
        },
        "interpretation_boundary": "This demonstrates only the behavior of the explicit deterministic abstraction-conditioned selector. It does not establish that the induced abstraction is semantically correct or that the observed consequence was learned from an external world.",
    }
    output = Path(".ci/experience-abstraction-consequence-loop.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
