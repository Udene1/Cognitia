from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState, EpistemicOutcome, Experience, ExperienceLedger, ExpectedConsequence, ObservedConsequence
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner

TRAIN = "The database outage caused the payment queue to stall. The database outage reduced worker throughput."
HELD_OUT = "The mirror coating change caused the telescope image to degrade. The mirror coating change reduced optical throughput."
REWIRED = "The mirror coating change caused the telescope image to degrade. The optical throughput reduced the mirror coating change."
FOLLOW_UP = "The telescope image did not improve after worker throughput increased."


def actions(problem: str):
    return tuple(reversed(ResearchSearchPlanner().plan(problem, max_actions=4).actions))


def make_experience():
    state = CognitiveState(problem=TRAIN)
    return Experience(
        experience_id="system-generated-1",
        prior_state=state,
        action=TRAIN,
        rationale="selected from generated candidate actions",
        expected=ExpectedConsequence("The causal structure should explain the observed outcome."),
        observed=ObservedConsequence("The causal structure did not explain the observed outcome.", EpistemicOutcome.REFUTED),
        state_update=CognitiveState(problem=TRAIN, evidence_ids=("training-refutation",)),
        provenance=("experience-downstream-consequence",),
    )


def run():
    selector = ExperienceAwareActionSelector()
    experience = make_experience()
    ledger = ExperienceLedger((experience,))

    held_with = selector.select(HELD_OUT, actions(HELD_OUT), ledger)
    held_without = selector.select(HELD_OUT, actions(HELD_OUT), ExperienceLedger())
    rewired_with = selector.select(REWIRED, actions(REWIRED), ledger)

    follow_state = CognitiveState(problem=FOLLOW_UP, evidence_ids=("training-refutation",))
    follow_with = selector.select(FOLLOW_UP, actions(FOLLOW_UP), ledger)
    follow_without = selector.select(FOLLOW_UP, actions(FOLLOW_UP), ExperienceLedger())

    result = {
        "question": "Does a bound experience with a changed outcome alter a later information-seeking action?",
        "training": TRAIN,
        "held_out": HELD_OUT,
        "rewired": REWIRED,
        "follow_up": FOLLOW_UP,
        "candidate_order_reversed": True,
        "researcher_expected_action": None,
        "researcher_hypothesis_ids": (),
        "researcher_uncertainty": (),
        "experience": {
            "id": experience.experience_id,
            "outcome": experience.observed.outcome.value,
            "state_update_evidence": list(experience.state_update.evidence_ids),
        },
        "held_out": {
            "with_experience": {
                "selected": held_with.selected.action.query.objective,
                "scores": [x.score for x in held_with.candidates],
                "relevant_ids": list(held_with.selected.relevant_experience_ids),
            },
            "without_experience": {
                "selected": held_without.selected.action.query.objective,
                "scores": [x.score for x in held_without.candidates],
            },
        },
        "rewired": {
            "relevant_ids": list(rewired_with.selected.relevant_experience_ids),
            "selected": rewired_with.selected.action.query.objective,
        },
        "follow_up": {
            "with_experience": {
                "selected": follow_with.selected.action.query.objective,
                "scores": [x.score for x in follow_with.candidates],
                "relevant_ids": list(follow_with.selected.relevant_experience_ids),
            },
            "without_experience": {
                "selected": follow_without.selected.action.query.objective,
                "scores": [x.score for x in follow_without.candidates],
            },
        },
        "observations": {
            "bound_experience_reaches_held_out": bool(held_with.selected.relevant_experience_ids),
            "rewired_control_rejects_experience": not bool(rewired_with.selected.relevant_experience_ids),
            "follow_up_action_changes": follow_with.selected.action.query.objective != follow_without.selected.action.query.objective,
            "follow_up_scores_change": [x.score for x in follow_with.candidates] != [x.score for x in follow_without.candidates],
        },
        "interpretation_boundary": "This measures the current deterministic experience-to-action bridge; it does not establish semantic understanding, autonomous learning, or cognition.",
    }
    path = Path(".ci/experience-downstream-consequence.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
