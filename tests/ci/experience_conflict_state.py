"""Zero-handholding test of contradictory experience as a cognitive state."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import (
    CognitiveState,
    EpistemicOutcome,
    Experience,
    ExperienceLedger,
    ExpectedConsequence,
    ObservedConsequence,
)
from cognitia.experience_abstraction import ExperienceAbstractionEngine
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner

PROBLEM = "The database outage caused the payment queue to stall. The database outage reduced worker throughput."
HELD_OUT = "The mirror coating change caused the telescope image to degrade. The mirror coating change reduced optical throughput."


def experience(experience_id: str, outcome: EpistemicOutcome) -> Experience:
    state = CognitiveState(problem=PROBLEM)
    return Experience(
        experience_id=experience_id,
        prior_state=state,
        action=PROBLEM,
        rationale="Selected by the existing action-selection mechanism.",
        expected=ExpectedConsequence("The causal structure should explain the observed outcome."),
        observed=ObservedConsequence(
            "The causal structure should explain the observed outcome."
            if outcome is EpistemicOutcome.CONFIRMED
            else "The causal structure did not explain the observed outcome.",
            outcome,
            evidence_ids=(f"evidence:{experience_id}",),
        ),
        state_update=state,
        provenance=("experience-conflict-state",),
    )


def select(ledger: ExperienceLedger) -> dict[str, object]:
    actions = tuple(reversed(ResearchSearchPlanner().plan(HELD_OUT, max_actions=4).actions))
    decision = ExperienceAwareActionSelector().select(HELD_OUT, actions, ledger)
    return {
        "selected": decision.selected.action.query.objective,
        "candidates": [
            {
                "objective": candidate.action.query.objective,
                "score": candidate.score,
                "relevant_experience_ids": list(candidate.relevant_experience_ids),
            }
            for candidate in decision.candidates
        ],
    }


def hypothesis_record(hypothesis) -> dict[str, object]:
    return {
        "features": list(hypothesis.features),
        "positive": hypothesis.positive,
        "negative": hypothesis.negative,
        "neutral": hypothesis.neutral,
        "observations": hypothesis.observations,
        "consistency": hypothesis.consistency,
    }


def main() -> None:
    confirmed = experience("confirmed", EpistemicOutcome.CONFIRMED)
    refuted = experience("refuted", EpistemicOutcome.REFUTED)
    engine = ExperienceAbstractionEngine()

    confirmed_hypotheses = engine.induce((confirmed,))
    contradictory_hypotheses = engine.induce((confirmed, refuted))

    conditions = {
        "confirmed_only": ExperienceLedger((confirmed,)),
        "refuted_only": ExperienceLedger((refuted,)),
        "contradictory": ExperienceLedger((confirmed, refuted)),
        "absent": ExperienceLedger(),
    }
    selections = {name: select(ledger) for name, ledger in conditions.items()}

    conflicts = [
        hypothesis_record(item)
        for item in contradictory_hypotheses
        if item.positive > 0 and item.negative > 0
    ]

    artifact = {
        "experiment": "experience-conflict-state",
        "research_question": "Does contradictory experience become an explicit unresolved cognitive state that changes what Cognitia does next, rather than merely cancelling action scores?",
        "handholding": {
            "expected_state": None,
            "expected_action": None,
            "expected_resolution": None,
            "expected_information_need": None,
        },
        "abstraction": {
            "confirmed_only": [hypothesis_record(item) for item in confirmed_hypotheses],
            "contradictory": [hypothesis_record(item) for item in contradictory_hypotheses],
            "explicit_conflict_hypotheses": conflicts,
        },
        "selection": selections,
        "comparison": {
            "contradictory_selected_differs_from_confirmed": selections["contradictory"]["selected"] != selections["confirmed_only"]["selected"],
            "contradictory_selected_differs_from_refuted": selections["contradictory"]["selected"] != selections["refuted_only"]["selected"],
            "contradictory_selected_differs_from_absent": selections["contradictory"]["selected"] != selections["absent"]["selected"],
            "explicit_conflict_state_present": bool(conflicts),
            "contradictory_candidate_scores_differ_from_absent": selections["contradictory"]["candidates"] != selections["absent"]["candidates"],
        },
    }
    path = Path(".ci/experience-conflict-state.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
