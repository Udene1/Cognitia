"""Held-out behavioral experiment with progressively reduced researcher control.

The harness supplies problems and an experience history, but never specifies the
expected action. The first episode establishes an action from Cognitia's own
planner. Later episodes reuse only the resulting experience record. Candidate
order is deliberately changed so list position cannot serve as the answer.

This is still an experiment around the current explicit selector. It does not
claim general cognition or learning.
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
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner, SearchAction


TRAIN_PROBLEM = "Why did the payment queue stall after a database outage?"
HELD_OUT_PROBLEM = "Why did the archive queue stall after a network outage?"


def actions(problem: str) -> list[SearchAction]:
    planned = list(ResearchSearchPlanner().plan(problem, max_actions=4).actions)
    # Remove the planner's convenient priority ordering. The selector must make
    # its choice from the same candidate set without receiving an expected index.
    return list(reversed(planned))


def make_experience(problem: str, selected: SearchAction, outcome: EpistemicOutcome, item_id: str) -> Experience:
    return Experience(
        experience_id=item_id,
        prior_state=CognitiveState(problem, hypothesis_ids=("cause",), uncertainty=("cause",)),
        action=selected.query.objective,
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
        provenance=("held-out-no-handholding-v1",),
    )


def run(name: str, problem: str, ledger: ExperienceLedger) -> dict:
    candidates = actions(problem)
    decision = ExperienceAwareActionSelector().select(problem, candidates, ledger)
    return {
        "condition": name,
        "problem": problem,
        "candidate_order": [item.query.objective for item in candidates],
        "selected": decision.selected.action.query.objective,
        "selected_purpose": decision.selected.action.purpose,
        "ranked": [
            {
                "objective": item.action.query.objective,
                "score": item.score,
                "relevant_experience_ids": list(item.relevant_experience_ids),
            }
            for item in decision.candidates
        ],
    }


def main() -> None:
    empty = ExperienceLedger()
    baseline = run("held_out_without_experience", HELD_OUT_PROBLEM, empty)

    # No action is authored into the experience. The action comes from the
    # system's own baseline trajectory on the training problem.
    training = run("experience_generation", TRAIN_PROBLEM, empty)
    generated_action = training["selected"]
    learned = ExperienceLedger((make_experience(TRAIN_PROBLEM, next(
        item for item in actions(TRAIN_PROBLEM) if item.query.objective == generated_action
    ), EpistemicOutcome.CONFIRMED, "generated-1"),))

    with_experience = run("held_out_with_related_experience", HELD_OUT_PROBLEM, learned)

    contradiction = ExperienceLedger((
        make_experience(TRAIN_PROBLEM, next(
            item for item in actions(TRAIN_PROBLEM) if item.query.objective == generated_action
        ), EpistemicOutcome.REFUTED, "contradiction-1"),
    ))
    after_contradiction = run("held_out_after_late_contradiction", HELD_OUT_PROBLEM, contradiction)

    artifact = {
        "experiment": "held-out-no-handholding-v1",
        "research_question": "Does experience-conditioned behavior survive when the problem changes, candidate ordering changes, and no expected action is authored?",
        "records": [baseline, training, with_experience, after_contradiction],
        "observations": {
            "experience_influence": baseline["selected"] != with_experience["selected"],
            "candidate_order_independent": baseline["candidate_order"] != with_experience["candidate_order"],
            "late_contradiction_changes_behavior": with_experience["selected"] != after_contradiction["selected"],
            "novel_held_out_selection": with_experience["selected"] not in {baseline["selected"], generated_action},
        },
        "researcher_controls_removed": [
            "no expected action is specified",
            "experience action is generated from the system's own training episode",
            "candidate order is reversed before selection",
            "held-out problem differs from the experience-generating problem",
        ],
        "boundary": "This remains a measurement of the explicit experience-to-action mechanism, not evidence of general cognition or learning.",
    }
    output = Path(".ci/held-out-no-handholding-research.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
