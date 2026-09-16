"""Experience abstraction v2: test whether representation invariance enables transfer."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ObservedConsequence
from cognitia.experience_abstraction import ExperienceAbstractionEngine


def make(item_id: str, problem: str, outcome: EpistemicOutcome) -> Experience:
    state = CognitiveState(problem)
    return Experience(
        experience_id=item_id,
        prior_state=state,
        action="search",
        rationale="selected by the preceding decision process",
        expected=ExpectedConsequence("reduce uncertainty"),
        observed=ObservedConsequence("reduce uncertainty", outcome),
        state_update=state,
        provenance=("induced-experience-abstraction-v2",),
    )


def main() -> None:
    engine = ExperienceAbstractionEngine()
    training = (
        make("why-after", "Why did the payment queue stall after the database outage?", EpistemicOutcome.CONFIRMED),
        make("explicit", "The database outage caused the payment queue to stall.", EpistemicOutcome.CONFIRMED),
        make("because", "The payment queue stalled because the database outage occurred.", EpistemicOutcome.CONFIRMED),
        make("negative-control", "Which alloy is suitable for a high-temperature turbine?", EpistemicOutcome.REFUTED),
    )
    induced = engine.induce(training)
    best = induced[0]

    held_out = make("held-out", "What caused the payment queue to stop?", EpistemicOutcome.CONFIRMED)
    unrelated = make("unrelated", "Which material is suitable for a lightweight bridge?", EpistemicOutcome.CONFIRMED)
    contradiction = make("contradiction", "The database outage caused the reporting queue to stop.", EpistemicOutcome.REFUTED)
    revised = engine.revise(induced, contradiction)
    revised_best = revised[0]

    records = {
        "training": [
            {"experience_id": item.experience_id, "features": list(engine.abstract(item).features)}
            for item in training
        ],
        "held_out": {
            "features": list(engine.abstract(held_out).features),
            "relevant_to_top": engine.relevant(best, held_out),
        },
        "unrelated": {
            "features": list(engine.abstract(unrelated).features),
            "relevant_to_top": engine.relevant(best, unrelated),
        },
        "before_contradiction": {
            "features": list(best.features),
            "positive": best.positive,
            "negative": best.negative,
            "consistency": best.consistency,
        },
        "after_contradiction": {
            "features": list(revised_best.features),
            "positive": revised_best.positive,
            "negative": revised_best.negative,
            "consistency": revised_best.consistency,
        },
    }
    artifact = {
        "experiment": "induced-experience-abstraction-v2",
        "research_question": "Does representation invariance allow an induced experience abstraction to transfer across causal surface forms and revise after contradiction without structural IDs?",
        "protocol": {
            "researcher_supplied_structural_ids": False,
            "researcher_supplied_expected_abstraction": False,
            "representation_layer": "candidate causal relation normalization",
        },
        "records": records,
        "observations": {
            "abstraction_induced": best.observations > 0,
            "top_is_causal": "causal" in best.features,
            "held_out_transfer": records["held_out"]["relevant_to_top"],
            "specificity_control": not records["unrelated"]["relevant_to_top"],
            "contradiction_changes_support": revised_best.consistency != best.consistency,
            "structural_ids_absent": True,
        },
        "interpretation_boundary": "This tests a deterministic abstraction mechanism over candidate language representations; it does not establish semantic understanding or truth of causal claims.",
    }
    output = Path(".ci/induced-experience-abstraction-v2.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
