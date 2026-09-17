from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState, EpistemicOutcome, Experience, ExperienceLedger, ExpectedConsequence, ObservedConsequence
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner

TRAIN = "The database outage caused the payment queue to stall. The database outage reduced worker throughput."
HELD_OUT = "The mirror coating change caused the telescope image to degrade. The mirror coating change reduced optical throughput."
REWIRED = "The mirror coating change caused the telescope image to degrade. The optical throughput reduced the mirror coating change."


def actions(problem: str):
    return tuple(reversed(ResearchSearchPlanner().plan(problem, max_actions=4).actions))


def make_experience(outcome: EpistemicOutcome) -> Experience:
    description = {
        EpistemicOutcome.CONFIRMED: "The causal structure explained the observed outcome.",
        EpistemicOutcome.REFUTED: "The causal structure did not explain the observed outcome.",
    }[outcome]
    return Experience(
        experience_id=f"system-generated-{outcome.value}",
        prior_state=CognitiveState(problem=TRAIN),
        action=TRAIN,
        rationale="selected from generated candidate actions",
        expected=ExpectedConsequence("The causal structure should explain the observed outcome."),
        observed=ObservedConsequence(description, outcome),
        state_update=CognitiveState(problem=TRAIN, evidence_ids=("training-result",)),
        provenance=("experience-evidence-boundary",),
    )


def snapshot(selector: ExperienceAwareActionSelector, problem: str, ledger: ExperienceLedger):
    decision = selector.select(problem, actions(problem), ledger)
    scores = [(item.action.query.objective, item.score) for item in decision.candidates]
    margin = decision.candidates[0].score - decision.candidates[1].score if len(decision.candidates) > 1 else None
    return {
        "selected": decision.selected.action.query.objective,
        "scores": scores,
        "margin_top1_top2": round(margin, 6) if margin is not None else None,
        "relevant_ids": list(decision.selected.relevant_experience_ids),
    }


def run():
    selector = ExperienceAwareActionSelector()
    empty = ExperienceLedger()
    confirmed = ExperienceLedger((make_experience(EpistemicOutcome.CONFIRMED),))
    refuted = ExperienceLedger((make_experience(EpistemicOutcome.REFUTED),))

    held = {
        "empty": snapshot(selector, HELD_OUT, empty),
        "confirmed": snapshot(selector, HELD_OUT, confirmed),
        "refuted": snapshot(selector, HELD_OUT, refuted),
    }
    rewired = {
        "confirmed": snapshot(selector, REWIRED, confirmed),
        "refuted": snapshot(selector, REWIRED, refuted),
    }

    result = {
        "question": "Does experience influence evidence evaluation itself, or merely act as a blindspot-avoidance signal before action selection?",
        "protocol": "Hold problem, candidate generation, structural relation and action-order constant; vary only the recorded epistemic outcome of the transferred experience.",
        "training": TRAIN,
        "held_out": HELD_OUT,
        "rewired": REWIRED,
        "candidate_order_reversed": True,
        "researcher_expected_action": None,
        "researcher_hypothesis_ids": (),
        "conditions": held,
        "rewired_control": rewired,
        "observations": {
            "confirmed_changes_scores_vs_empty": held["confirmed"]["scores"] != held["empty"]["scores"],
            "refuted_changes_scores_vs_empty": held["refuted"]["scores"] != held["empty"]["scores"],
            "confirmed_changes_action_vs_empty": held["confirmed"]["selected"] != held["empty"]["selected"],
            "refuted_changes_action_vs_empty": held["refuted"]["selected"] != held["empty"]["selected"],
            "confirmed_and_refuted_have_different_scores": held["confirmed"]["scores"] != held["refuted"]["scores"],
            "confirmed_and_refuted_have_different_actions": held["confirmed"]["selected"] != held["refuted"]["selected"],
            "rewired_rejects_confirmed": not bool(rewired["confirmed"]["relevant_ids"]),
            "rewired_rejects_refuted": not bool(rewired["refuted"]["relevant_ids"]),
        },
        "interpretation_boundary": "This isolates the current deterministic experience-to-action bridge. It does not establish semantic understanding, autonomous learning, or cognition.",
    }
    path = Path(".ci/experience-evidence-boundary.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
