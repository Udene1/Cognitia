"""Isolate communication consequence evidence integration from unsupported factor domains."""
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
        return WebResearchBundle(QUESTION, (search,), self.documents[:fetch_limit])


def _research(documents: tuple[EnvironmentObservation, ...]) -> OpenResearchResult:
    return OpenEndedResearch(web=FixtureWeb(documents)).investigate(
        QUESTION,
        max_rounds=1,
        search_results=1,
        documents_per_round=len(documents),
        claims_per_document=10,
    )


def _observation(case: str, content: str) -> EnvironmentObservation:
    return EnvironmentObservation(
        id=f"recipient-consequence:{case}",
        source="independent_recipient_environment",
        content=content,
        metadata=(("recipient", "operator"), ("experiment", "communication_consequence_supported_domain")),
    )


def _case(baseline: OpenResearchResult, synthesis: ResearchSynthesis, case: str, content: str) -> dict[str, object]:
    consequence = _observation(case, content)
    consequence_result = _research((consequence,))
    augmented = baseline.augment(consequence_result)
    updated_synthesis = ResearchSynthesisEngine().synthesize(augmented)
    core = AnsweringCore()
    previous = core.build(synthesis)
    updated, revision = core.revise(
        previous,
        updated_synthesis,
        new_evidence=tuple(claim.proposition for claim in consequence_result.claims),
    )
    return {
        "case": case,
        "consequence": content,
        "extracted_claims": [claim.proposition for claim in consequence_result.claims],
        "claim_relations": [claim.relations for claim in consequence_result.claims],
        "factor_names": [factor.factor for factor in updated_synthesis.factors],
        "factor_domains": [factor.domain for factor in updated_synthesis.factors],
        "synthesis_status": updated_synthesis.status,
        "previous_fingerprint": revision.previous_fingerprint,
        "new_fingerprint": revision.new_fingerprint,
        "revision_changed": revision.changed,
        "answer": updated.answer,
        "next_actions": list(updated.what_would_change_answer),
    }


def main() -> None:
    baseline_documents = (
        EnvironmentObservation(
            id="baseline:resource",
            source="baseline_source:resource",
            content="Systemic resource exhaustion caused the service collapse.",
            reliability=0.7,
        ),
        EnvironmentObservation(
            id="baseline:dependency",
            source="baseline_source:dependency",
            content="Systemic dependency failure caused the service collapse.",
            reliability=0.7,
        ),
    )
    baseline = _research(baseline_documents)
    synthesis = ResearchSynthesisEngine().synthesize(baseline)

    relevant = _case(
        baseline,
        synthesis,
        "discriminating-causal-consequence",
        "The systemic dependency timeout caused the service collapse; CPU remained below its limit during the same interval.",
    )
    unrelated = _case(
        baseline,
        synthesis,
        "unrelated-observation",
        "The dashboard color changed during the incident, and the display was updated during the outage.",
    )

    artifact = {
        "experiment": "communication_consequence_supported_domain",
        "question": "When extracted recipient consequences already fall within the existing synthesis domain taxonomy, can the ordinary evidence path change synthesis and answer state without communication-specific interpretation?",
        "handholding": {
            "expected_relevance": None,
            "expected_interpretation": None,
            "expected_state_change": None,
            "expected_answer": None,
            "communication_learning_rule": None,
        },
        "baseline": {
            "claims": [claim.proposition for claim in baseline.claims],
            "factor_names": [factor.factor for factor in synthesis.factors],
            "factor_domains": [factor.domain for factor in synthesis.factors],
            "synthesis_status": synthesis.status,
            "answer": AnsweringCore().build(synthesis).answer,
        },
        "cases": [relevant, unrelated],
        "comparison": {
            "both_start_from_supported_baseline": all(domain != "other" for domain in [factor.domain for factor in synthesis.factors]),
            "relevant_added_factor": len(relevant["factor_names"]) > len(synthesis.factors),
            "unrelated_added_factor": len(unrelated["factor_names"]) > len(synthesis.factors),
            "relevant_revision_changed": relevant["revision_changed"],
            "unrelated_revision_changed": unrelated["revision_changed"],
            "relevant_answer_differs_from_unrelated": relevant["answer"] != unrelated["answer"],
        },
        "observations": [
            "The existing domain taxonomy was not modified.",
            "Recipient consequences entered as raw EnvironmentObservation objects.",
            "The existing claim extraction, genealogy, augmentation, synthesis, and answer revision paths were used.",
            "No relevance or desired state change was supplied to Cognitia.",
        ],
    }
    path = Path(".ci/communication-consequence-supported-domain.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
