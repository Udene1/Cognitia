"""Differential test of raw communication consequences at the existing cognition boundary.

No consequence is translated into a claim, success/failure label, preferred act,
or learning rule. The same prior cognitive state receives two different raw
recipient consequences and the existing machinery is allowed to show whether
content alone changes extraction or revision.
"""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.answering import AnsweringCore
from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.research_synthesis import FactorExplanation, ResearchSynthesis


QUESTION = "Why did service X fail?"


def _initial_synthesis() -> ResearchSynthesis:
    return ResearchSynthesis(
        question=QUESTION,
        status="candidate_multi_factor_synthesis",
        thesis="Two candidate contributors remain unresolved.",
        factors=(
            FactorExplanation(
                factor="resource exhaustion",
                contribution="resource exhaustion contributed to the failure",
                claim_ids=("seed-resource",),
                source_count=1,
                origin_count=1,
                confidence="candidate",
                domain="systemic",
                origin_ids=("seed-resource-origin",),
            ),
            FactorExplanation(
                factor="dependency failure",
                contribution="dependency failure contributed to the failure",
                claim_ids=("seed-dependency",),
                source_count=1,
                origin_count=1,
                confidence="candidate_uncertain",
                domain="systemic",
                origin_ids=("seed-dependency-origin",),
            ),
        ),
        complementary_domains=("systemic",),
        competing_explanations=(),
        distinguishing_evidence=(
            "a trace separating resource exhaustion from dependency failure",
        ),
        caveats=("The relative importance of the candidates is unresolved.",),
        next_actions=("Acquire the discriminating trace.",),
    )


def _observation(recipient: str, payload: str) -> EnvironmentObservation:
    return EnvironmentObservation(
        id=f"communication:{recipient}",
        source="independent_recipient_environment",
        content=payload,
        metadata=(
            ("recipient", recipient),
            ("experiment", "communication_consequence_differential"),
        ),
    )


def _run_case(core: AnsweringCore, synthesis: ResearchSynthesis, recipient: str, payload: str) -> dict[str, object]:
    observation = _observation(recipient, payload)
    extracted = DocumentClaimExtractor().extract(observation)
    previous = core.build(synthesis)
    updated, revision = core.revise(previous, synthesis, new_evidence=(observation.content,))
    return {
        "recipient": recipient,
        "observation_id": observation.id,
        "payload": payload,
        "extracted_claims": [
            {
                "id": claim.id,
                "proposition": claim.proposition,
                "confidence": claim.confidence,
                "polarity": claim.polarity,
            }
            for claim in extracted
        ],
        "claim_count": len(extracted),
        "revision_changed": revision.changed,
        "revision_changed_because": list(revision.changed_because),
        "previous_fingerprint": revision.previous_fingerprint,
        "new_fingerprint": revision.new_fingerprint,
        "new_answer": updated.answer,
        "next_actions_unchanged": updated.what_would_change_answer == previous.what_would_change_answer,
    }


def main() -> None:
    synthesis = _initial_synthesis()
    core = AnsweringCore()

    # The experiment does not tell Cognitia which response is relevant. The
    # distinction is deliberately visible only in the research fixture itself.
    cases = (
        (
            "operator",
            "The discriminating trace shows the dependency timeout occurred first; CPU stayed below its limit during the same interval.",
        ),
        (
            "operator",
            "The dashboard color changed during the incident, but no additional trace or timing evidence was recorded.",
        ),
    )
    results = [_run_case(core, synthesis, recipient, payload) for recipient, payload in cases]

    artifact = {
        "experiment": "communication_consequence_differential",
        "question": "Does the semantic content of an unparsed recipient consequence change Cognitia's existing extraction or revision behavior?",
        "handholding": {
            "expected_interpretation": None,
            "expected_revision": None,
            "expected_success_or_failure_label": None,
            "communication_learning_rule": None,
        },
        "baseline": {
            "answer": core.build(synthesis).answer,
            "next_actions": list(core.build(synthesis).what_would_change_answer),
        },
        "cases": results,
        "comparison": {
            "claim_count_equal": results[0]["claim_count"] == results[1]["claim_count"],
            "revision_changed_equal": results[0]["revision_changed"] == results[1]["revision_changed"],
            "fingerprints_equal": results[0]["new_fingerprint"] == results[1]["new_fingerprint"],
            "answers_equal": results[0]["new_answer"] == results[1]["new_answer"],
        },
        "observations": [
            "Both recipient responses entered through EnvironmentObservation.",
            "DocumentClaimExtractor ran without a communication-specific interpretation rule.",
            "AnsweringCore.revise received raw consequence text without a supplied synthesis update.",
            "No consequence was labeled as successful, unsuccessful, relevant, or irrelevant for Cognitia.",
        ],
    }
    path = Path(".ci/communication-consequence-differential.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
