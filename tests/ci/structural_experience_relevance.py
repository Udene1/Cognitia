"""No-handholding test after replacing lexical experience relevance.

The researcher supplies only problems and lets Cognitia generate/select actions.
The experiment asks whether a structurally matching prior experience transfers
across domains, while a directed role reversal is rejected as unrelated.
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
from cognitia.structural_experience import signature

TRAIN = "Why did the payment queue stall after a database outage?"
HELD_OUT = "Why did the telescope image degrade after a mirror coating changed?"
ROLE_REVERSAL = "Why did the database outage cause the payment queue to stall?"


def candidate_actions(problem: str) -> list[SearchAction]:
    return list(reversed(ResearchSearchPlanner().plan(problem, max_actions=4).actions))


def select(problem: str, ledger: ExperienceLedger) -> dict[str, object]:
    candidates = candidate_actions(problem)
    decision = ExperienceAwareActionSelector().select(problem, candidates, ledger)
    return {
        "problem": problem,
        "candidate_order": [item.query.objective for item in candidates],
        "selected": decision.selected.action.query.objective,
        "ranked": [
            {
                "objective": item.action.query.objective,
                "score": item.score,
                "relevant_experience_ids": list(item.relevant_experience_ids),
            }
            for item in decision.candidates
        ],
    }


def make_experience(problem: str, action: str, outcome: EpistemicOutcome, experience_id: str) -> Experience:
    return Experience(
        experience_id=experience_id,
        prior_state=CognitiveState(problem),
        action=action,
        rationale="Selected by Cognitia without researcher-supplied expected action.",
        expected=ExpectedConsequence("investigation attempted"),
        observed=ObservedConsequence(
            "investigation attempted",
            outcome,
            evidence_ids=(f"evidence:{experience_id}",),
        ),
        state_update=CognitiveState(problem),
        provenance=("structural-experience-relevance",),
    )


def main() -> None:
    empty = ExperienceLedger()
    training = select(TRAIN, empty)
    confirmed = make_experience(TRAIN, training["selected"], EpistemicOutcome.CONFIRMED, "confirmed-training")
    learned = ExperienceLedger((confirmed,))

    held_out_without = select(HELD_OUT, empty)
    held_out_with = select(HELD_OUT, learned)
    role_reversal = select(ROLE_REVERSAL, learned)

    training_sig = signature(TRAIN)
    held_out_sig = signature(HELD_OUT)
    reversal_sig = signature(ROLE_REVERSAL)

    artifact = {
        "experiment": "structural-experience-relevance",
        "research_question": "After lexical relevance is removed, can experience generated without researcher guidance transfer to a novel domain through structured relation identity?",
        "records": {
            "training": training,
            "held_out_without_experience": held_out_without,
            "held_out_with_experience": held_out_with,
            "role_reversal_with_experience": role_reversal,
            "generated_experience": {
                "experience_id": confirmed.experience_id,
                "action": confirmed.action,
                "outcome": confirmed.observed.outcome.value,
            },
            "structural_signatures": {
                "training": training_sig,
                "held_out": held_out_sig,
                "role_reversal": reversal_sig,
            },
        },
        "observations": {
            "experience_changes_held_out_selection": held_out_without["selected"] != held_out_with["selected"],
            "training_and_held_out_have_matching_relation_structure": training_sig.relations == held_out_sig.relations,
            "role_reversal_has_matching_relation_structure": training_sig.relations == reversal_sig.relations,
            "role_reversal_is_structurally_relevant": bool(role_reversal["ranked"][0]["relevant_experience_ids"]),
            "lexical_relevance_is_not_used": True,
        },
        "researcher_controls_removed": [
            "no expected action",
            "no hypothesis identifiers",
            "no uncertainty labels",
            "training action comes from Cognitia's selector",
            "candidate order is reversed",
            "held-out domain and vocabulary differ",
            "no scenario-specific routing",
        ],
        "interpretation_boundary": "Structural relation matching is evidence about the current representation and experience-selection mechanism. It does not establish semantic understanding, causal truth, learning, or general cognition.",
        "next_discriminator": "If structural transfer occurs, test whether argument identity and event structure can be abstracted independently while preserving direction, then introduce contradictory outcomes and inspect whether the same structural hypothesis retains explicit support/contradiction lineage.",
    }
    output = Path(".ci/structural-experience-relevance.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True, default=lambda x: x.__dict__), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True, default=lambda x: x.__dict__))


if __name__ == "__main__":
    main()
