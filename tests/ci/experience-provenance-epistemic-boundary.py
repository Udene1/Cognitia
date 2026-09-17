"""Held-out experiment: experience enters active state, then Cognitia chooses.

The harness supplies a prior experience and its observed outcome because this
boundary is specifically testing the transition from recorded experience into
active state. It does not supply an expected operation, expected answer, or
routing rule for the held-out problem.
"""
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
from cognitia.experience_state import apply_experience_to_state
from cognitia.information_need import InformationNeedDetector
from cognitia.operation_selection import OperationOption, OperationSelector
from cognitia.state_action_generation import AvailableOperation

ARTIFACT = Path(".ci/experience-provenance-epistemic-boundary.json")

OPTIONS = (
    OperationOption(AvailableOperation("search", "use external evidence"), cost=0.40),
    OperationOption(AvailableOperation("inspect", "inspect local evidence"), cost=0.20),
    OperationOption(AvailableOperation("compute", "compute a result"), cost=0.10),
    OperationOption(AvailableOperation("reason", "reason over existing evidence"), cost=0.05),
)


def prior_experience(outcome: EpistemicOutcome) -> Experience:
    return Experience(
        experience_id=f"exp-pump-{outcome.value}",
        prior_state=CognitiveState(problem="pump control failed under load"),
        action="test pressure-response mechanism",
        rationale="A previous intervention produced an observable consequence.",
        expected=ExpectedConsequence(description="pressure remains stable"),
        observed=ObservedConsequence(
            description=(
                "pressure remains stable"
                if outcome is not EpistemicOutcome.REFUTED
                else "pressure becomes unstable"
            ),
            outcome=outcome,
        ),
        state_update=CognitiveState(
            problem="pump control failed under load",
            hypothesis_ids=("mechanism:pressure-response",),
        ),
        provenance=("direct-observation",),
    )


def run_condition(outcome: EpistemicOutcome) -> dict[str, object]:
    base = CognitiveState(
        problem="new thermal-control problem with related feedback structure",
        knowledge_ids=("knowledge:independent",),
        uncertainty=("unknown:new-problem",),
        self_model_ids=("self-model:available-capabilities",),
        other_model_ids=("world-model:thermal-system",),
    )
    experience = prior_experience(outcome)
    transition = apply_experience_to_state(base, experience)
    need = InformationNeedDetector().detect(transition.resulting_state)
    choice = OperationSelector().assess(transition.resulting_state, need, OPTIONS)

    return {
        "outcome": outcome.value,
        "prior_experience_id": experience.experience_id,
        "held_out_problem": transition.resulting_state.problem,
        "state_before": {
            "knowledge_ids": list(base.knowledge_ids),
            "experience_ids": list(base.experience_ids),
            "hypothesis_ids": list(base.hypothesis_ids),
            "uncertainty": list(base.uncertainty),
            "self_model_ids": list(base.self_model_ids),
            "other_model_ids": list(base.other_model_ids),
        },
        "state_after_experience": {
            "knowledge_ids": list(transition.resulting_state.knowledge_ids),
            "experience_ids": list(transition.resulting_state.experience_ids),
            "hypothesis_ids": list(transition.resulting_state.hypothesis_ids),
            "uncertainty": list(transition.resulting_state.uncertainty),
            "self_model_ids": list(transition.resulting_state.self_model_ids),
            "other_model_ids": list(transition.resulting_state.other_model_ids),
        },
        "transition": {
            "changed": transition.changed,
            "source": transition.source.value,
            "epistemically_established": transition.epistemically_established,
            "requires_epistemic_test": transition.requires_epistemic_test,
            "reason": transition.reason,
        },
        "information_need": {
            "kind": need.kind.value,
            "reasons": list(need.reasons),
            "confidence": need.confidence,
        },
        "operation_assessments": [
            {
                "operation": item.operation.name,
                "expected_state_improvement": item.expected_state_improvement,
                "cost": item.cost,
                "risk": item.risk,
                "net_value": item.net_value,
                "reasons": list(item.reasons),
            }
            for item in choice.assessments
        ],
        "selected_operation": choice.selected.operation.name if choice.selected else None,
    }


def main() -> None:
    records = [
        run_condition(EpistemicOutcome.CONFIRMED),
        run_condition(EpistemicOutcome.REFUTED),
    ]

    artifact = {
        "experiment": "experience-provenance-epistemic-boundary-v1",
        "research_question": "When retrieved experience changes active state, can Cognitia preserve its distinction from knowledge, self-model and other/world-model information while still routing the held-out problem through epistemic processing?",
        "researcher_controlled_inputs": [
            "prior experience identity and observed outcome",
            "held-out problem",
            "available operations and costs",
        ],
        "researcher_did_not_supply": [
            "expected operation",
            "expected answer",
            "expected information-need classification",
            "expected ranking",
        ],
        "records": records,
        "structural_checks": {
            "knowledge_preserved": all(r["state_after_experience"]["knowledge_ids"] == r["state_before"]["knowledge_ids"] for r in records),
            "experience_separate": all(r["state_after_experience"]["experience_ids"] == [r["prior_experience_id"]] for r in records),
            "self_model_preserved": all(r["state_after_experience"]["self_model_ids"] == r["state_before"]["self_model_ids"] for r in records),
            "other_model_preserved": all(r["state_after_experience"]["other_model_ids"] == r["state_before"]["other_model_ids"] for r in records),
            "epistemic_test_required": all(r["transition"]["requires_epistemic_test"] for r in records),
            "operation_selection_executed": all(r["selected_operation"] is not None for r in records),
        },
        "interpretation": "This artifact records whether the new transition preserves provenance and what the existing information-need detector and operation selector actually do afterward. The selected operation is evidence about the implemented mechanism, not proof of understanding.",
        "next_boundary": "Remove the researcher-supplied prior experience and observed outcome. Let Cognitia encounter and record an experience through its own interaction loop, then test whether that self-generated experience is transferred to a genuinely new problem without researcher-authored routing.",
    }

    assert all(r["transition"]["changed"] for r in records)
    assert artifact["structural_checks"]["knowledge_preserved"]
    assert artifact["structural_checks"]["experience_separate"]
    assert artifact["structural_checks"]["self_model_preserved"]
    assert artifact["structural_checks"]["other_model_preserved"]
    assert artifact["structural_checks"]["epistemic_test_required"]
    assert artifact["structural_checks"]["operation_selection_executed"]

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
