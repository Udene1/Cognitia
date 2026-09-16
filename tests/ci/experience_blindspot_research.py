"""Behavioral experiment for experience influence, contradiction, and recovery.

The experiment deliberately supplies candidate actions rather than an expected
choice. Experience changes only the ranking evidence; the harness records the
actual selection. A condition is informative even when the observed behavior
does not match the research hypothesis.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import runpy

from cognitia.experience import (
    CognitiveState,
    EpistemicOutcome,
    ExpectedConsequence,
    Experience,
    ExperienceLedger,
    ObservedConsequence,
)
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner


PROBLEM_A = "Why did the payment queue stall after a database outage?"
PROBLEM_B = "Why did the archive queue stall after a network outage?"


def action_set(problem: str):
    return ResearchSearchPlanner().plan(
        problem,
        max_actions=2,
    ).actions


def experience(item_id: str, problem: str, action: str, outcome: EpistemicOutcome) -> Experience:
    return Experience(
        experience_id=item_id,
        prior_state=CognitiveState(problem, hypothesis_ids=("cause",), uncertainty=("cause",)),
        action=action,
        rationale="The preceding state left the cause unresolved.",
        expected=ExpectedConsequence("the selected investigation will clarify the cause"),
        observed=ObservedConsequence(
            "the selected investigation will clarify the cause",
            outcome,
            evidence_ids=(f"evidence:{item_id}",),
        ),
        state_update=CognitiveState(
            problem,
            hypothesis_ids=("cause",),
            uncertainty=() if outcome is EpistemicOutcome.CONFIRMED else ("cause",),
        ),
        provenance=("experience-blindspot-research",),
    )


def run_condition(name: str, problem: str, ledger: ExperienceLedger):
    actions = action_set(problem)
    decision = ExperienceAwareActionSelector().select(problem, actions, ledger)
    return {
        "condition": name,
        "problem": problem,
        "candidates": [
            {
                "objective": item.action.query.objective,
                "purpose": item.action.purpose,
                "score": item.score,
                "relevant_experience_ids": list(item.relevant_experience_ids),
                "rationale": item.rationale,
            }
            for item in decision.candidates
        ],
        "selected": decision.selected.action.query.objective,
        "selected_purpose": decision.selected.action.purpose,
        "experience_ids": [item.experience_id for item in ledger.all()],
    }


def main() -> None:
    planner = ResearchSearchPlanner()
    baseline_ledger = ExperienceLedger()
    baseline = run_condition("experience_absent", PROBLEM_A, baseline_ledger)

    prior_actions = planner.plan(PROBLEM_A, max_actions=2).actions
    old_action = prior_actions[0].query.objective
    present_ledger = ExperienceLedger((experience("x-confirmed", PROBLEM_A, old_action, EpistemicOutcome.CONFIRMED),))
    present = run_condition("experience_present", PROBLEM_A, present_ledger)

    conflict_ledger = ExperienceLedger(
        (
            experience("x-confirmed", PROBLEM_A, old_action, EpistemicOutcome.CONFIRMED),
            experience("x-refuted-1", PROBLEM_A, old_action, EpistemicOutcome.REFUTED),
            experience("x-refuted-2", PROBLEM_A, old_action, EpistemicOutcome.REFUTED),
        )
    )
    conflict = run_condition("conflicting_evidence", PROBLEM_A, conflict_ledger)

    recovery_ledger = ExperienceLedger(
        conflict_ledger.all()
        + (
            experience("x-recovered", PROBLEM_B, planner.plan(PROBLEM_B, max_actions=2).actions[-1].query.objective, EpistemicOutcome.CONFIRMED),
        )
    )
    recovery = run_condition("recovery_after_contradiction", PROBLEM_B, recovery_ledger)

    records = [baseline, present, conflict, recovery]
    observation = {
        "influence": baseline["selected"] != present["selected"],
        "transfer": present["selected"] != baseline["selected"] and recovery["selected"] != baseline["selected"],
        "defeasibility": conflict["selected"] != present["selected"],
        "recovery": recovery["selected"] != conflict["selected"],
        "novelty": recovery["selected"] not in {item["selected"] for item in (baseline, present)},
        "persistence": False,
        "note": "Persistence requires a subsequent independent episode and is not claimed by this four-condition run.",
    }
    artifact = {
        "experiment": "experience-conditioned-future-behavior-v1",
        "research_question": "Can prior experience influence a new problem without becoming an unconditional routing rule?",
        "conditions": records,
        "observations": observation,
        "interpretation_boundary": "This experiment measures the behavior of the explicit experience-to-action mechanism. It does not establish general cognition or learning.",
    }

    namespace = runpy.run_path("tests/ci/experience_abstraction_consequence_loop.py")
    namespace["main"]()
    loop_path = Path(".ci/experience-abstraction-consequence-loop.json")
    artifact["experience_abstraction_consequence_loop"] = json.loads(loop_path.read_text(encoding="utf-8"))

    output = Path(".ci/experience-blindspot-research.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
