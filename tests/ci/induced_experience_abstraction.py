"""Experiment: can transferable experience abstractions emerge without state IDs?

The researcher provides only raw problem surfaces, actions and observed outcomes.
No hypothesis/evidence identifiers are supplied to the abstraction engine.
"""
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
        provenance=("induced-experience-abstraction",),
    )


def main() -> None:
    engine = ExperienceAbstractionEngine()
    training = (
        make("causal-1", "Why did the payment queue stall after a database outage?", EpistemicOutcome.CONFIRMED),
        make("causal-2", "The network outage caused the archive service to stop.", EpistemicOutcome.CONFIRMED),
        make("noncausal-1", "Which alloy is suitable for a high-temperature turbine?", EpistemicOutcome.REFUTED),
    )
    induced = engine.induce(training)
    best = induced[0]

    held_out = make("held-out", "Why did the telemetry pipeline stop after a certificate rotation?", EpistemicOutcome.CONFIRMED)
    unrelated = make("unrelated", "Which material is suitable for a lightweight bridge?", EpistemicOutcome.CONFIRMED)

    contradiction = make("contradiction", "Why did the reporting queue stop after a schema migration?", EpistemicOutcome.REFUTED)
    revised = engine.revise(induced, contradiction)
    revised_best = revised[0]

    artifact = {
        "experiment": "induced-experience-abstraction-v1",
        "research_question": "Can Cognitia construct a transferable structural abstraction from experience surfaces without researcher-supplied state identifiers, and revise its support after contradiction?",
        "protocol": {
            "researcher_supplied_structural_ids": False,
            "researcher_supplied_expected_abstraction": False,
            "input": "raw problem surfaces + action + observed epistemic outcome",
            "candidate_feature_families": list(engine.FEATURE_FAMILIES),
        },
        "training": [
            {"experience_id": item.experience_id, "features": list(engine.abstract(item).features)}
            for item in training
        ],
        "top_before_contradiction": {
            "features": list(best.features),
            "positive": best.positive,
            "negative": best.negative,
            "neutral": best.neutral,
            "consistency": best.consistency,
        },
        "held_out": {
            "features": list(engine.abstract(held_out).features),
            "relevant_to_top": engine.relevant(best, held_out),
        },
        "unrelated": {
            "features": list(engine.abstract(unrelated).features),
            "relevant_to_top": engine.relevant(best, unrelated),
        },
        "after_contradiction": {
            "features": list(engine.abstract(contradiction).features),
            "top_features": list(revised_best.features),
            "positive": revised_best.positive,
            "negative": revised_best.negative,
            "neutral": revised_best.neutral,
            "consistency": revised_best.consistency,
            "top_changed": revised_best.features != best.features,
        },
    }
    artifact["observations"] = {
        "abstraction_induced": best.observations > 0,
        "held_out_transfer": artifact["held_out"]["relevant_to_top"],
        "specificity_control": not artifact["unrelated"]["relevant_to_top"],
        "contradiction_changes_support": revised_best.consistency != best.consistency,
        "structural_ids_absent": True,
    }

    output = Path(".ci/induced-experience-abstraction.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
