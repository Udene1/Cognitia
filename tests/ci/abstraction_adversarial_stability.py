"""Adversarial stability experiment for contradiction-driven abstraction revision."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ObservedConsequence
from cognitia.experience_abstraction import ExperienceAbstractionEngine, AbstractionHypothesis


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
        provenance=("abstraction-adversarial-stability",),
    )


def state_of(engine: ExperienceAbstractionEngine, hypotheses: tuple[AbstractionHypothesis, ...], label: str, held_out: Experience) -> dict:
    selected = hypotheses[0]
    return {
        "label": label,
        "selected_features": list(selected.features),
        "feature_count": len(selected.features),
        "positive": selected.positive,
        "negative": selected.negative,
        "consistency": selected.consistency,
        "held_out_relevant": engine.relevant(selected, held_out),
    }


def main() -> None:
    engine = ExperienceAbstractionEngine()
    seed = (
        make("why-after", "Why did the payment queue stall after the database outage?", EpistemicOutcome.CONFIRMED),
        make("explicit", "The database outage caused the payment queue to stall.", EpistemicOutcome.CONFIRMED),
        make("because", "The payment queue stalled because the database outage occurred.", EpistemicOutcome.CONFIRMED),
        make("negative-control", "Which alloy is suitable for a high-temperature turbine?", EpistemicOutcome.REFUTED),
    )
    held_out = make("held-out", "Why did the telemetry queue stop after a certificate rotation?", EpistemicOutcome.CONFIRMED)
    hypotheses = engine.induce(seed)
    trajectory = [state_of(engine, hypotheses, "initial", held_out)]

    contradictions = (
        make("contradiction-1", "The database outage caused the reporting queue to stop.", EpistemicOutcome.REFUTED),
        make("contradiction-2", "Why did the archive queue stop after the network outage?", EpistemicOutcome.REFUTED),
        make("contradiction-3", "The certificate rotation caused the telemetry queue to stop.", EpistemicOutcome.REFUTED),
    )
    for index, contradiction in enumerate(contradictions, start=1):
        hypotheses = engine.revise(hypotheses, contradiction)
        trajectory.append(state_of(engine, hypotheses, f"after_contradiction_{index}", held_out))

    artifact = {
        "experiment": "abstraction-adversarial-stability-v1",
        "research_question": "Does contradiction-driven abstraction narrowing remain stable under adversarial counterexamples, or does the mechanism overfit by repeatedly specializing?",
        "protocol": {
            "researcher_supplied_structural_ids": False,
            "researcher_supplied_expected_abstraction": False,
            "adversarial_counterexamples": len(contradictions),
        },
        "trajectory": trajectory,
        "observations": {
            "initial_abstraction_is_broad": trajectory[0]["selected_features"] == ["causal"],
            "narrowing_occurred": any(item["feature_count"] > trajectory[0]["feature_count"] for item in trajectory[1:]),
            "repeated_narrowing": trajectory[-1]["feature_count"] > trajectory[1]["feature_count"],
            "held_out_transfer_survives": all(item["held_out_relevant"] for item in trajectory),
            "support_decreases": trajectory[-1]["consistency"] < trajectory[0]["consistency"],
        },
        "interpretation_boundary": "Feature specialization after contradiction is not treated as learning unless it remains stable and useful on held-out experiences under adversarial counterexamples.",
    }
    output = Path(".ci/abstraction-adversarial-stability.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
