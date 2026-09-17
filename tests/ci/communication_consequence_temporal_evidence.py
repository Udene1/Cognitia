"""Test whether non-causal temporal consequence evidence reaches synthesis."""
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
        QUESTION, max_rounds=1, search_results=1,
        documents_per_round=len(documents), claims_per_document=10,
    )


def _observe(case: str, content: str) -> EnvironmentObservation:
    return EnvironmentObservation(
        id=f"recipient-consequence:{case}",
        source="independent_recipient_environment",
        content=content,
        metadata=(("recipient", "operator"), ("experiment", "communication_consequence_temporal_evidence")),
    )


def _case(baseline: OpenResearchResult, synthesis: ResearchSynthesis, case: str, content: str) -> dict[str, object]:
    observation = _observe(case, content)
    consequence_result = _research((observation,))
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
        "claims": [
            {
                "proposition": claim.proposition,
                "relations": claim.relations,
                "temporal_markers": claim.temporal_markers,
            }
            for claim in consequence_result.claims
        ],
        "factor_names": [factor.factor for factor in updated_synthesis.factors],
        "synthesis_status": updated_synthesis.status,
        "answer": updated.answer,
        "revision_changed": revision.changed,
        "previous_fingerprint": revision.previous_fingerprint,
        "new_fingerprint": revision.new_fingerprint,
    }


def main() -> None:
    baseline_documents = (
        EnvironmentObservation("baseline:resource", "baseline_source:resource", "Internal resource exhaustion caused the service collapse.", 0.7),
        EnvironmentObservation("baseline:dependency", "baseline_source:dependency", "Internal dependency failure caused the service collapse.", 0.7),
    )
    baseline = _research(baseline_documents)
    synthesis = ResearchSynthesisEngine().synthesize(baseline)

    temporal = _case(
        baseline, synthesis, "temporal-consequence",
        "The internal dependency timeout was observed before the service collapse. CPU remained below its limit during the same interval.",
    )
    unrelated = _case(
        baseline, synthesis, "unrelated-observation",
        "The dashboard color changed during the incident, and the display was updated during the outage.",
    )

    artifact = {
        "experiment": "communication_consequence_temporal_evidence",
        "question": "Can a recipient consequence that expresses timing but not an explicit causal connective cross the existing evidence path into synthesis?",
        "handholding": {
            "expected_interpretation": None,
            "expected_relevance": None,
            "expected_causal_relationship": None,
            "expected_state_change": None,
            "communication_learning_rule": None,
        },
        "baseline": {
            "factor_names": [factor.factor for factor in synthesis.factors],
            "answer": AnsweringCore().build(synthesis).answer,
        },
        "cases": [temporal, unrelated],
        "comparison": {
            "temporal_claim_extracted": bool(temporal["claims"]),
            "temporal_added_factor": len(temporal["factor_names"]) > len(synthesis.factors),
            "unrelated_added_factor": len(unrelated["factor_names"]) > len(synthesis.factors),
            "answers_differ": temporal["answer"] != unrelated["answer"],
        },
    }
    path = Path(".ci/communication-consequence-temporal-evidence.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
