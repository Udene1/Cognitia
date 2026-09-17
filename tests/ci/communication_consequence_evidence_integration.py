"""Test whether an extracted recipient consequence can cross the ordinary evidence path.

The experiment does not translate a response into a communication-specific meaning.
It lets the existing environment observation, claim extraction, research synthesis,
and answer revision machinery operate on two raw consequences with the same prior
research state. The only controlled perturbation is the consequence content.
"""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.answering import AnsweringCore
from cognitia.environment import EnvironmentObservation
from cognitia.open_research import OpenEndedResearch, OpenResearchResult
from cognitia.research_synthesis import ResearchSynthesis, ResearchSynthesisEngine
from cognitia.web_research import WebResearchBundle


QUESTION = "Why did service X fail?"


class FixtureWeb:
    """Controlled environment source; Cognitia receives raw documents only."""

    def __init__(self, documents: tuple[EnvironmentObservation, ...]):
        self.documents = documents

    def investigate(self, question: str, *, limit: int, fetch_limit: int) -> WebResearchBundle:
        search = EnvironmentObservation(
            id=f"search:{question}",
            source="fixture_environment",
            content=question,
            reliability=0.7,
            metadata=(("kind", "search_result"), ("query", question)),
        )
        return WebResearchBundle(
            QUESTION,
            (search,),
            self.documents[:fetch_limit],
        )


def _research(documents: tuple[EnvironmentObservation, ...]) -> OpenResearchResult:
    return OpenEndedResearch(web=FixtureWeb(documents)).investigate(
        QUESTION,
        max_rounds=1,
        search_results=1,
        documents_per_round=len(documents),
        claims_per_document=10,
    )


def _observe(case: str, content: str) -> EnvironmentObservation:
    return EnvironmentObservation(
        id=f"recipient-consequence:{case}",
        source="independent_recipient_environment",
        content=content,
        metadata=(
            ("recipient", "operator"),
            ("experiment", "communication_consequence_evidence_integration"),
        ),
    )


def _run_case(
    baseline: OpenResearchResult,
    baseline_synthesis: ResearchSynthesis,
    case: str,
    consequence: EnvironmentObservation,
) -> dict[str, object]:
    consequence_result = _research((consequence,))
    augmented = baseline.augment(consequence_result)
    updated_synthesis = ResearchSynthesisEngine().synthesize(augmented)
    previous = AnsweringCore().build(baseline_synthesis)
    updated, revision = AnsweringCore().revise(
        previous,
        updated_synthesis,
        new_evidence=tuple(claim.proposition for claim in consequence_result.claims),
    )
    return {
        "case": case,
        "consequence": consequence.content,
        "extracted_claims": [
            {
                "id": claim.id,
                "proposition": claim.proposition,
                "confidence": claim.confidence,
                "polarity": claim.polarity,
                "relations": claim.relations,
            }
            for claim in consequence_result.claims
        ],
        "claim_count": len(consequence_result.claims),
        "augmented_claim_count": len(augmented.claims),
        "synthesis": updated_synthesis.render(),
        "factor_names": [factor.factor for factor in updated_synthesis.factors],
        "previous_fingerprint": revision.previous_fingerprint,
        "new_fingerprint": revision.new_fingerprint,
        "revision_changed": revision.changed,
        "revision_changed_because": list(revision.changed_because),
        "answer": updated.answer,
        "next_actions": list(updated.what_would_change_answer),
    }


def main() -> None:
    baseline_documents = (
        EnvironmentObservation(
            id="baseline:resource",
            source="baseline_source:resource",
            content="Resource exhaustion caused the service collapse.",
            reliability=0.7,
        ),
        EnvironmentObservation(
            id="baseline:dependency",
            source="baseline_source:dependency",
            content="A dependency failure caused the service collapse.",
            reliability=0.7,
        ),
    )
    baseline = _research(baseline_documents)
    baseline_synthesis = ResearchSynthesisEngine().synthesize(baseline)

    relevant = _run_case(
        baseline,
        baseline_synthesis,
        "discriminating-causal-consequence",
        _observe(
            "relevant",
            "The dependency timeout caused the service collapse; CPU remained below its limit during the same interval.",
        ),
    )
    unrelated = _run_case(
        baseline,
        baseline_synthesis,
        "unrelated-observation",
        _observe(
            "unrelated",
            "The dashboard color changed during the incident, and the display was updated during the outage.",
        ),
    )

    artifact = {
        "experiment": "communication_consequence_evidence_integration",
        "question": "Can a recipient consequence that becomes an ordinary extracted claim cross the existing evidence and synthesis path and change the answer state?",
        "handholding": {
            "expected_interpretation": None,
            "expected_relevance": None,
            "expected_state_change": None,
            "expected_answer": None,
            "communication_learning_rule": None,
        },
        "baseline": {
            "claims": [claim.proposition for claim in baseline.claims],
            "factor_names": [factor.factor for factor in baseline_synthesis.factors],
            "answer": AnsweringCore().build(baseline_synthesis).answer,
        },
        "cases": [relevant, unrelated],
        "comparison": {
            "claim_count_differs": relevant["claim_count"] != unrelated["claim_count"],
            "relevant_revision_changed": relevant["revision_changed"],
            "unrelated_revision_changed": unrelated["revision_changed"],
            "relevant_fingerprint_differs_from_baseline": relevant["new_fingerprint"] != relevant["previous_fingerprint"],
            "unrelated_fingerprint_differs_from_baseline": unrelated["new_fingerprint"] != unrelated["previous_fingerprint"],
            "answers_differ": relevant["answer"] != unrelated["answer"],
        },
        "observations": [
            "Recipient consequences entered as EnvironmentObservation objects.",
            "The existing OpenEndedResearch evidence path performed claim extraction and genealogy without a communication-specific interpreter.",
            "The baseline and consequence research results were combined through OpenResearchResult.augment().",
            "AnsweringCore.revise received only the extracted claim propositions as new evidence; no relevance or desired state change was supplied.",
        ],
    }
    path = Path(".ci/communication-consequence-evidence-integration.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
