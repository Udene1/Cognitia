"""Stress test that removes the convenient action semantics from evaluation.

The experiment does not tell the selector which action should win. It changes
surface wording, weakens lexical relation between prior and current problems,
introduces contradiction after an earlier confirmed episode, and records the
full candidate trajectory. The current planner remains the action generator;
this experiment therefore measures robustness of the existing bridge rather
than general learning.
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

TRAIN = "Why did invoice processing stop after the primary database became unavailable?"
HELD_OUT = "What caused archival jobs to cease following a storage-service interruption?"
CONTRADICTED = "What caused archival jobs to resume after the storage-service interruption?"


def candidates(problem: str) -> list[SearchAction]:
    # The experiment deliberately destroys the planner's normal ordering.
    return list(reversed(ResearchSearchPlanner().plan(problem, max_actions=4).actions))


def exp(problem: str, action: SearchAction, outcome: EpistemicOutcome, ident: str) -> Experience:
    return Experience(
        experience_id=ident,
        prior_state=CognitiveState(problem, hypothesis_ids=("cause",), uncertainty=("cause",)),
        action=action.query.objective,
        rationale="The current state left the causal explanation unresolved.",
        expected=ExpectedConsequence("the investigation will reduce uncertainty"),
        observed=ObservedConsequence(
            "the investigation will reduce uncertainty",
            outcome,
            evidence_ids=(f"evidence:{ident}",),
        ),
        state_update=CognitiveState(
            problem,
            hypothesis_ids=("cause",),
            uncertainty=() if outcome is EpistemicOutcome.CONFIRMED else ("cause",),
        ),
        provenance=("action-space-reduction-v1",),
    )


def run(label: str, problem: str, ledger: ExperienceLedger) -> dict:
    pool = candidates(problem)
    decision = ExperienceAwareActionSelector().select(problem, pool, ledger)
    return {
        "condition": label,
        "problem": problem,
        "candidates": [a.query.objective for a in pool],
        "ranked": [
            {
                "objective": x.action.query.objective,
                "score": x.score,
                "experience_ids": list(x.relevant_experience_ids),
                "rationale": x.rationale,
            }
            for x in decision.candidates
        ],
        "selected": decision.selected.action.query.objective,
    }


def main() -> None:
    empty = ExperienceLedger()
    train = run("training_episode", TRAIN, empty)
    generated = next(a for a in candidates(TRAIN) if a.query.objective == train["selected"])

    confirmed = ExperienceLedger((exp(TRAIN, generated, EpistemicOutcome.CONFIRMED, "confirmed-1"),))
    held_out = run("weakly_related_held_out", HELD_OUT, confirmed)

    # Contradiction arrives as a later observation of the same experience.
    revised = ExperienceLedger((exp(TRAIN, generated, EpistemicOutcome.REFUTED, "confirmed-1-revised"),))
    contradicted = run("after_late_contradiction", HELD_OUT, revised)

    partial = ExperienceLedger((exp(TRAIN, generated, EpistemicOutcome.PARTIAL, "partial-1"),))
    partial_run = run("partial_evidence", CONTRADICTED, partial)

    artifact = {
        "experiment": "action-space-reduction-v1",
        "research_question": "What survives when surface similarity weakens, contradiction is delayed, and candidate ordering is unhelpful?",
        "records": [train, held_out, contradicted, partial_run],
        "observations": {
            "weak_relation_influence": held_out["selected"] != run("held_out_baseline", HELD_OUT, empty)["selected"],
            "late_contradiction_changes_selection": held_out["selected"] != contradicted["selected"],
            "partial_evidence_is_distinct": partial_run["selected"] != contradicted["selected"],
            "action_space_was_researcher_authored": True,
        },
        "next_reduction": "Replace planner-authored search facets with actions generated from the current state, uncertainty, hypotheses, and observed consequences; the evaluator must not prescribe the intermediate action vocabulary.",
        "boundary": "No result here establishes general cognition, learning, or transfer. The experiment measures the current explicit mechanism under reduced experimental convenience.",
    }
    output = Path(".ci/action-space-reduction-research.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
