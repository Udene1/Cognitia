"""No-handholding test of repeated-argument binding across domains."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ExperienceLedger, ObservedConsequence
from cognitia.experience_decision import ExperienceAwareActionSelector
from cognitia.research_search import ResearchSearchPlanner
from cognitia.structural_experience import signature, structural_signature_matches

TRAIN = "The database outage caused the payment queue to stall. The database outage reduced worker throughput."
HELD_OUT = "The mirror coating change caused the telescope image to degrade. The mirror coating change reduced optical throughput."
BINDING_REVERSED = "The mirror coating change caused the telescope image to degrade. The optical throughput reduced the mirror coating change."


def select(problem: str, ledger: ExperienceLedger) -> dict[str, object]:
    actions = list(reversed(ResearchSearchPlanner().plan(problem, max_actions=4).actions))
    decision = ExperienceAwareActionSelector().select(problem, actions, ledger)
    return {"problem": problem, "candidate_order": [a.query.objective for a in actions], "selected": decision.selected.action.query.objective, "ranked": [{"objective": a.action.query.objective, "score": a.score, "relevant_experience_ids": list(a.relevant_experience_ids)} for a in decision.candidates]}


def experience(problem: str, action: str) -> Experience:
    return Experience(
        experience_id="binding-training",
        prior_state=CognitiveState(problem),
        action=action,
        rationale="Selected by Cognitia without researcher-supplied expected action.",
        expected=ExpectedConsequence("investigation attempted"),
        observed=ObservedConsequence("investigation attempted", EpistemicOutcome.CONFIRMED, evidence_ids=("evidence:binding-training",)),
        state_update=CognitiveState(problem),
        provenance=("relational-binding-experience",),
    )


def main() -> None:
    empty = ExperienceLedger()
    training = select(TRAIN, empty)
    learned = ExperienceLedger((experience(TRAIN, training["selected"]),))
    held_out = select(HELD_OUT, learned)
    binding_reversed = select(BINDING_REVERSED, learned)

    train_sig, held_sig, reversed_sig = signature(TRAIN), signature(HELD_OUT), signature(BINDING_REVERSED)
    held_relevant = any("binding-training" in x["relevant_experience_ids"] for x in held_out["ranked"])
    reversed_relevant = any("binding-training" in x["relevant_experience_ids"] for x in binding_reversed["ranked"])

    artifact = {
        "experiment": "relational-binding-experience",
        "research_question": "Can experience transfer across domains when lexical identity is abstracted but repeated-argument binding is preserved?",
        "records": {"training": training, "held_out_with_experience": held_out, "binding_reversed_with_experience": binding_reversed, "structural_signatures": {"training": train_sig, "held_out": held_sig, "binding_reversed": reversed_sig}},
        "observations": {
            "binding_preserving_signature_matches": structural_signature_matches(train_sig, held_sig),
            "binding_reversed_signature_matches": structural_signature_matches(train_sig, reversed_sig),
            "held_out_experience_relevant": held_relevant,
            "binding_reversed_experience_relevant": reversed_relevant,
            "lexical_argument_identity_used_for_matching": False,
        },
        "controls_removed": ["expected action", "hypothesis identifiers", "uncertainty labels", "lexical overlap matching", "scenario-specific routing"],
        "interpretation_boundary": "This tests structural representation and experience relevance, not semantic understanding, causal truth, learning, or general cognition.",
        "next_discriminator": "If binding-preserving transfer and binding-reversed rejection both occur, test whether a changed or contradictory outcome updates only the bound experience pattern and propagates to a later action or information need.",
    }
    output = Path(".ci/relational-binding-experience.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True, default=lambda x: x.__dict__), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True, default=lambda x: x.__dict__))


if __name__ == "__main__":
    main()
