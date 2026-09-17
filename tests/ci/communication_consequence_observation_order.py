"""Test whether event ordering can be reconstructed from observation metadata."""
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


def _observe(case: str, content: str, observed_at: str) -> EnvironmentObservation:
    return EnvironmentObservation(
        id=f"recipient-consequence:{case}:{observed_at}",
        source="independent_recipient_environment",
        content=content,
        reliability=0.8,
        metadata=(
            ("recipient", "operator"),
            ("experiment", "communication_consequence_observation_order"),
            ("observed_at", observed_at),
        ),
    )


def _case(
    baseline: OpenResearchResult,
    synthesis: ResearchSynthesis,
    case: str,
    observations: tuple[EnvironmentObservation, ...],
) -> dict[str, object]:
    consequence_result = _research(observations)
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
        "observations": [
            {
                "content": observation.content,
                "observed_at": dict(observation.metadata).get("observed_at"),
            }
            for observation in observations
        ],
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

    ordered = _case(
        baseline,
        synthesis,
        "ordered-events",
        (
            _observe("ordered-events", "The internal dependency timeout occurred.", "2026-09-17T10:00:00Z"),
            _observe("ordered-events", "The service collapse occurred.", "2026-09-17T10:01:00Z"),
        ),
    )
    reversed_order = _case(
        baseline,
        synthesis,
        "reversed-events",
        (
            _observe("reversed-events", "The internal dependency timeout occurred.", "2026-09-17T10:01:00Z"),
            _observe("reversed-events", "The service collapse occurred.", "2026-09-17T10:00:00Z"),
        ),
    )

    artifact = {
        "experiment": "communication_consequence_observation_order",
        "question": "Can Cognitia derive a usable relationship from multiple independent observations whose ordering is carried by observation metadata rather than temporal language?",
        "handholding": {
            "expected_interpretation": None,
            "expected_relevance": None,
            "expected_relationship": None,
            "expected_state_change": None,
            "communication_learning_rule": None,
        },
        "baseline": {
            "factor_names": [factor.factor for factor in synthesis.factors],
            "answer": AnsweringCore().build(synthesis).answer,
        },
        "cases": [ordered, reversed_order],
        "comparison": {
            "ordered_claim_count": len(ordered["claims"]),
            "reversed_claim_count": len(reversed_order["claims"]),
            "factor_sets_differ": ordered["factor_names"] != reversed_order["factor_names"],
            "answers_differ": ordered["answer"] != reversed_order["answer"],
            "ordered_added_factor": len(ordered["factor_names"]) > len(synthesis.factors),
            "reversed_added_factor": len(reversed_order["factor_names"]) > len(synthesis.factors),
        },
    }
    path = Path(".ci/communication-consequence-observation-order.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
