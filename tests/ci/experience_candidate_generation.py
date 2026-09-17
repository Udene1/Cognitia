"""Measure whether stored experience can suppress candidate generation.

This experiment intentionally does not modify StateActionGenerator to accept
experience. The question is whether the current architecture exposes a path
from the experience ledger into candidate generation. We run the same held-out
states and available operations with no experience, a structurally related
confirmed experience, and a structurally related refuted experience, while
recording the retrieved experience and the complete pre-selection candidate
sets.

A stable candidate set across the three conditions is evidence about the
implemented boundary only: experience currently does not reach the generator
through the tested path. It is not evidence that candidate-generation
blindspots are impossible in a different architecture or through state
mutation.
"""
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
from cognitia.state_action_generation import AvailableOperation, StateActionGenerator


ARTIFACT = Path(".ci/experience-candidate-generation.json")


def experience_for(outcome: EpistemicOutcome) -> Experience:
    prior = CognitiveState(
        problem="determine whether the service's deployment evidence is current",
        evidence_ids=("deployment-evidence",),
        hypothesis_ids=("h-deployment-current",),
        uncertainty=("freshness is unresolved",),
        goal="establish deployment evidence status",
    )
    observed = ObservedConsequence(
        description="deployment evidence was not current",
        outcome=outcome,
        evidence_ids=("deployment-result",),
    )
    return Experience(
        experience_id=f"exp-{outcome.value}",
        prior_state=prior,
        action="inspect deployment evidence",
        rationale="The deployment evidence required direct inspection.",
        expected=ExpectedConsequence(
            description="deployment evidence was current",
            evidence_ids=("deployment-evidence",),
        ),
        observed=observed,
        state_update=prior,
        provenance=("experience-candidate-generation",),
    )


def signature(candidate) -> dict[str, object]:
    return {
        "operation": candidate.operation.name,
        "capability": candidate.operation.capability,
        "objective": candidate.objective,
        "source_signals": list(candidate.source_signals),
        "rationale": candidate.rationale,
    }


def run_case(name: str, state: CognitiveState, ledger: ExperienceLedger) -> dict[str, object]:
    operations = (
        AvailableOperation("external-search", "external evidence search"),
        AvailableOperation("inspect", "local inspection"),
        AvailableOperation("compute", "computation"),
        AvailableOperation("reason", "reasoning"),
    )
    retrieved = ledger.relevant_to(
        evidence_ids=state.evidence_ids,
        hypothesis_ids=state.hypothesis_ids,
    )
    candidates = StateActionGenerator().generate(state, operations, max_actions=32)
    return {
        "case": name,
        "state": {
            "problem": state.problem,
            "evidence_ids": list(state.evidence_ids),
            "knowledge_ids": list(state.knowledge_ids),
            "hypothesis_ids": list(state.hypothesis_ids),
            "uncertainty": list(state.uncertainty),
            "goal": state.goal,
        },
        "retrieved_experience_ids": [item.experience_id for item in retrieved],
        "candidate_count": len(candidates),
        "candidates": [signature(item) for item in candidates],
    }


def main() -> None:
    held_out_cases = (
        (
            "freshness-required",
            CognitiveState(
                problem="determine whether the service's deployment evidence is current today",
                evidence_ids=("deployment-evidence",),
                hypothesis_ids=("h-deployment-current",),
                uncertainty=("current status is unresolved",),
                goal="establish current deployment evidence status",
            ),
        ),
        (
            "local-uncertainty",
            CognitiveState(
                problem="determine why the deployment evidence is inconsistent",
                evidence_ids=("deployment-evidence",),
                hypothesis_ids=("h-deployment-current",),
                uncertainty=("local discrepancy is unresolved",),
                goal="identify the local cause of the discrepancy",
            ),
        ),
        (
            "computation",
            CognitiveState(
                problem="calculate the deployment evidence age in days",
                evidence_ids=("deployment-evidence",),
                hypothesis_ids=("h-deployment-current",),
                uncertainty=("age calculation is unresolved",),
                goal="calculate evidence age",
            ),
        ),
    )

    conditions = {
        "absent": ExperienceLedger(),
        "confirmed": ExperienceLedger((experience_for(EpistemicOutcome.CONFIRMED),)),
        "refuted": ExperienceLedger((experience_for(EpistemicOutcome.REFUTED),)),
    }

    cases: list[dict[str, object]] = []
    for case_name, state in held_out_cases:
        for condition, ledger in conditions.items():
            result = run_case(case_name, state, ledger)
            result["experience_condition"] = condition
            cases.append(result)

    by_case: dict[str, dict[str, list[dict[str, object]]]] = {}
    for result in cases:
        by_case.setdefault(result["case"], {})[result["experience_condition"]] = result

    comparisons = []
    for case_name, conditions_by_name in by_case.items():
        absent = conditions_by_name["absent"]["candidates"]
        confirmed = conditions_by_name["confirmed"]["candidates"]
        refuted = conditions_by_name["refuted"]["candidates"]
        comparisons.append(
            {
                "case": case_name,
                "absent_equals_confirmed": absent == confirmed,
                "absent_equals_refuted": absent == refuted,
                "confirmed_equals_refuted": confirmed == refuted,
                "candidate_set_changed": not (absent == confirmed == refuted),
                "experience_retrieved_when_confirmed": bool(
                    conditions_by_name["confirmed"]["retrieved_experience_ids"]
                ),
                "experience_retrieved_when_refuted": bool(
                    conditions_by_name["refuted"]["retrieved_experience_ids"]
                ),
                "operation_names": sorted({item["operation"] for item in absent}),
            }
        )

    all_invariant = all(not item["candidate_set_changed"] for item in comparisons)
    record = {
        "experiment": "experience-candidate-generation",
        "research_question": "Can structurally related experience prevent a necessary investigation candidate from being generated?",
        "conditions": ["absent", "confirmed", "refuted"],
        "generator_boundary": "StateActionGenerator receives current state and available operations; experience is not an input.",
        "cases": cases,
        "comparisons": comparisons,
        "candidate_generation_invariant_across_experience": all_invariant,
        "interpretation": (
            "Across the tested held-out states, the complete pre-selection candidate set was invariant "
            "to absence, confirmation, or refutation of a structurally related retrieved experience. "
            "This establishes that the current StateActionGenerator path does not consume the experience ledger "
            "and therefore cannot suppress candidates through direct experience input. It does not establish "
            "that experience can never create a generation blindspot through a future state-update or learning path."
            if all_invariant
            else
            "At least one held-out state produced a different pre-selection candidate set across experience "
            "conditions. This identifies a candidate-generation blindspot path that requires investigation before "
            "treating the boundary as invariant."
        ),
        "next_boundary": (
            "Test whether an experience-derived state update can alter the inputs to candidate generation without "
            "encoding the expected candidate set in the experiment."
        ),
    }

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
