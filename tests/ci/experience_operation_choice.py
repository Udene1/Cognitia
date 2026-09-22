"""Experiment for the experience -> epistemic-operation boundary.

The harness deliberately supplies no expected operation or action. It records
whether the existing experience bridge changes upstream action evaluation and
whether the existing information-need/operation-selection path changes as a
consequence.
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
from cognitia.information_need import InformationNeedDetector
from cognitia.operation_selection import OperationOption, OperationSelector
from cognitia.research_search import ResearchSearchPlanner
from cognitia.state_action_generation import AvailableOperation


CASES = (
    (
        "fresh_external",
        CognitiveState(
            "What is the current status of the payment queue after the database outage?",
            hypothesis_ids=("cause",),
            uncertainty=("cause",),
        ),
        "What was the recent status of the archive queue after the network outage?",
    ),
    (
        "unresolved_local",
        CognitiveState(
            "Why did the payment queue stall after a database outage?",
            hypothesis_ids=("cause",),
            uncertainty=("cause",),
        ),
        "Why did the archive queue stall after a network outage?",
    ),
    (
        "computation",
        CognitiveState(
            "Calculate the expected recovery time from the observed queue delay.",
            hypothesis_ids=("recovery",),
            uncertainty=("recovery",),
        ),
        "Calculate the expected archive recovery time from the observed delay.",
    ),
)

OPERATIONS = (
    OperationOption(AvailableOperation("reason", "reason from existing evidence")),
    OperationOption(AvailableOperation("inspect", "inspect local evidence")),
    OperationOption(AvailableOperation("external-search", "search external evidence")),
    OperationOption(AvailableOperation("compute", "compute from available quantities")),
)


def experience(item_id: str, problem: str, action: str, outcome: EpistemicOutcome) -> Experience:
    return Experience(
        experience_id=item_id,
        prior_state=CognitiveState(
            problem,
            hypothesis_ids=("cause",),
            uncertainty=("cause",),
        ),
        action=action,
        rationale="The prior episode left the cause unresolved.",
        expected=ExpectedConsequence("the selected investigation will clarify the cause"),
        observed=ObservedConsequence(
            "the selected investigation will clarify the cause",
            outcome,
            evidence_ids=(f"evidence:{item_id}",),
        ),
        state_update=CognitiveState(
            problem,
            hypothesis_ids=("cause",),
            uncertainty=() if outcome is EpistemicOutcome.CONFIRMED else ("cause",),
        ),
        provenance=("experience-operation-choice-research",),
    )


def action_snapshot(problem: str, ledger: ExperienceLedger) -> dict:
    actions = ResearchSearchPlanner().plan(problem, max_actions=2).actions
    decision = ExperienceAwareActionSelector().select(problem, actions, ledger)
    return {
        "selected": decision.selected.action.query.objective,
        "selected_purpose": decision.selected.action.purpose,
        "candidates": [
            {
                "objective": item.action.query.objective,
                "purpose": item.action.purpose,
                "score": item.score,
                "relevant_experience_ids": list(item.relevant_experience_ids),
                "rationale": item.rationale,
            }
            for item in decision.candidates
        ],
    }


def operation_snapshot(state: CognitiveState) -> dict:
    need = InformationNeedDetector().detect(state)
    choice = OperationSelector().assess(state, need, OPERATIONS)
    return {
        "information_need": {
            "kind": need.kind.value,
            "confidence": need.confidence,
            "reasons": list(need.reasons),
        },
        "selected": choice.selected.operation.name if choice.selected else None,
        "assessments": [
            {
                "operation": item.operation.name,
                "capability": item.operation.capability,
                "expected_state_improvement": item.expected_state_improvement,
                "cost": item.cost,
                "risk": item.risk,
                "net_value": item.net_value,
                "reasons": list(item.reasons),
            }
            for item in choice.assessments
        ],
    }


def main() -> None:
    records: list[dict] = []
    for case_name, state, prior_problem in CASES:
        planner = ResearchSearchPlanner()
        prior_actions = planner.plan(prior_problem, max_actions=2).actions
        prior_action = prior_actions[0].query.objective

        conditions = (
            ("experience_absent", ExperienceLedger()),
            (
                "experience_confirmed",
                ExperienceLedger((experience(f"{case_name}-confirmed", prior_problem, prior_action, EpistemicOutcome.CONFIRMED),)),
            ),
            (
                "experience_refuted",
                ExperienceLedger((experience(f"{case_name}-refuted", prior_problem, prior_action, EpistemicOutcome.REFUTED),)),
            ),
        )

        case_records = []
        for condition, ledger in conditions:
            case_records.append(
                {
                    "condition": condition,
                    "experience_ids": [item.experience_id for item in ledger.all()],
                    "action_trajectory": action_snapshot(state.problem, ledger),
                    "operation_trajectory": operation_snapshot(state),
                }
            )
        records.append(
            {
                "case": case_name,
                "state": {
                    "problem": state.problem,
                    "hypothesis_ids": list(state.hypothesis_ids),
                    "uncertainty": list(state.uncertainty),
                    "evidence_ids": list(state.evidence_ids),
                },
                "conditions": case_records,
                "observations": {
                    "action_selection_changed_with_experience": len({item["action_trajectory"]["selected"] for item in case_records}) > 1,
                    "information_need_changed_with_experience": len({item["operation_trajectory"]["information_need"]["kind"] for item in case_records}) > 1,
                    "operation_selection_changed_with_experience": len({item["operation_trajectory"]["selected"] for item in case_records}) > 1,
                },
            }
        )

    artifact = {
        "experiment": "experience-operation-choice-boundary-v1",
        "research_question": "Can a structurally related prior experience interfere with epistemic operation choice when the new problem requires fresh evidence?",
        "operation_options": [
            {"name": option.operation.name, "capability": option.operation.capability, "cost": option.cost, "risk": option.risk}
            for option in OPERATIONS
        ],
        "cases": records,
        "interpretation_boundary": "The experiment observes the current implemented path. It does not establish that experience can never influence operation choice through another architecture or interaction path, and it does not establish general cognition.",
    }

    output = Path(".ci/experience-operation-choice.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
