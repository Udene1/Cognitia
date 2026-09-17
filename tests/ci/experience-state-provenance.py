"""Experiment: experience changes active state without becoming truth."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import (
    CognitiveState,
    EpistemicOutcome,
    ExpectedConsequence,
    Experience,
    ObservedConsequence,
)
from cognitia.experience_state import ClaimSource, apply_experience_to_state

ARTIFACT = Path(".ci/experience-state-provenance.json")


def experience(outcome: EpistemicOutcome) -> Experience:
    return Experience(
        experience_id=f"exp-{outcome.value}",
        prior_state=CognitiveState(problem="novel structurally related problem"),
        action="test candidate mechanism",
        rationale="A prior experience supplied a relevant expectation.",
        expected=ExpectedConsequence(description="mechanism succeeds"),
        observed=ObservedConsequence(
            description="mechanism succeeds" if outcome is not EpistemicOutcome.REFUTED else "mechanism fails",
            outcome=outcome,
        ),
        state_update=CognitiveState(
            problem="novel structurally related problem",
            hypothesis_ids=(f"experience:{outcome.value}",),
        ),
        provenance=("direct-observation",),
    )


def main() -> None:
    base = CognitiveState(
        problem="novel structurally related problem",
        knowledge_ids=("knowledge:independent",),
        uncertainty=("unknown:novel-problem",),
    )

    confirmed = apply_experience_to_state(base, experience(EpistemicOutcome.CONFIRMED))
    refuted = apply_experience_to_state(base, experience(EpistemicOutcome.REFUTED))

    record = {
        "experiment": "experience-state-provenance",
        "research_question": "Can experience modify active cognitive state while remaining distinguishable from established knowledge and still requiring epistemic testing?",
        "base_state": {
            "knowledge_ids": list(base.knowledge_ids),
            "uncertainty": list(base.uncertainty),
            "hypothesis_ids": list(base.hypothesis_ids),
        },
        "confirmed_experience": {
            "changed": confirmed.changed,
            "source": confirmed.source.value,
            "knowledge_preserved": confirmed.resulting_state.knowledge_ids == base.knowledge_ids,
            "experience_recorded_as_hypothesis": "experience:exp-confirmed" in confirmed.resulting_state.hypothesis_ids,
            "epistemically_established": confirmed.epistemically_established,
            "requires_epistemic_test": confirmed.requires_epistemic_test,
        },
        "refuted_experience": {
            "changed": refuted.changed,
            "source": refuted.source.value,
            "knowledge_preserved": refuted.resulting_state.knowledge_ids == base.knowledge_ids,
            "refutation_preserved_as_uncertainty": "refuted-experience:exp-refuted" in refuted.resulting_state.uncertainty,
            "epistemically_established": refuted.epistemically_established,
            "requires_epistemic_test": refuted.requires_epistemic_test,
        },
        "interpretation": "The boundary permits experience to alter active state, but only through provenance-bearing hypotheses or uncertainty. It never promotes Experience.state_update into knowledge and always marks the resulting state for epistemic testing.",
        "next_boundary": "Feed the resulting state into Cognitia's existing epistemic operation-selection path on a genuinely new problem and observe whether experience-derived, knowledge, self-model, and other-model information remain distinguishable during investigation.",
    }

    assert confirmed.changed
    assert confirmed.source is ClaimSource.EXPERIENCE
    assert confirmed.resulting_state.knowledge_ids == base.knowledge_ids
    assert confirmed.requires_epistemic_test
    assert not confirmed.epistemically_established
    assert refuted.changed
    assert refuted.source is ClaimSource.UNCERTAINTY
    assert refuted.resulting_state.knowledge_ids == base.knowledge_ids
    assert "refuted-experience:exp-refuted" in refuted.resulting_state.uncertainty
    assert refuted.requires_epistemic_test
    assert not refuted.epistemically_established

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
