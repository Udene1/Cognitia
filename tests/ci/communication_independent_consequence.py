"""Expose independent recipient consequences to existing observation machinery."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.answering import AnsweringCore
from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.research_synthesis import FactorExplanation, ResearchSynthesis

INITIAL = ResearchSynthesis(
    question="Why did service X fail?",
    status="candidate_multi_factor_synthesis",
    thesis="The current evidence identifies multiple candidate contributors.",
    factors=(
        FactorExplanation("resource exhaustion", "resource exhaustion contributed to the failure", ("claim:resource",), 1, 1, "candidate", "systemic", ("origin:initial",)),
        FactorExplanation("dependency failure", "dependency failure contributed to the failure", ("claim:dependency",), 1, 1, "candidate_uncertain", "systemic", ("origin:initial",)),
    ),
    complementary_domains=("systemic",),
    competing_explanations=(),
    distinguishing_evidence=("a trace separating resource exhaustion from dependency failure",),
    caveats=("The relative importance of the candidates is unresolved.",),
    next_actions=("Acquire the discriminating trace.",),
)

# No effectiveness label, preferred act, or expected interpretation is supplied.
RESPONSES = (
    EnvironmentObservation(
        "recipient-consequence:operator", "independent_recipient_environment",
        "I inspected the dependency trace. The timeout preceded the restart. CPU remained below its limit during the same interval.",
        metadata=(("recipient", "operator"),),
    ),
    EnvironmentObservation(
        "recipient-consequence:learner", "independent_recipient_environment",
        "The trace shows the dependency timeout before the restart. Memory remained below its limit during the event.",
        metadata=(("recipient", "learner"),),
    ),
    EnvironmentObservation(
        "recipient-consequence:decision_maker", "independent_recipient_environment",
        "After rollback, availability returned while the dependency error persisted. The rollback did not remove the dependency error.",
        metadata=(("recipient", "decision_maker"),),
    ),
)


def main() -> None:
    previous = AnsweringCore().build(INITIAL)
    extractor = DocumentClaimExtractor()
    interactions = []
    for observation in RESPONSES:
        claims = extractor.extract(observation)
        interactions.append({
            "recipient": dict(observation.metadata)["recipient"],
            "consequence": observation.content,
            "observation_id": observation.id,
            "claims": [
                {
                    "id": claim.id,
                    "proposition": claim.proposition,
                    "confidence": claim.confidence,
                    "polarity": claim.polarity,
                    "relations": claim.relations,
                    "uncertainty_markers": claim.uncertainty_markers,
                }
                for claim in claims
            ],
            "claim_count": len(claims),
        })

    artifact = {
        "experiment": "communication_independent_consequence",
        "question": "When an independent recipient consequence arrives as an environment observation, what does the existing observation boundary actually extract?",
        "handholding": {
            "expected_communication_strategy": None,
            "expected_effective_message": None,
            "expected_consequence": None,
            "expected_interpretation": None,
            "expected_state_change": None,
            "learning_rule": None,
        },
        "initial_answer": previous.render(),
        "interactions": interactions,
        "observations": [
            "Recipient responses entered through EnvironmentObservation.",
            "DocumentClaimExtractor ran without a communication-specific interpretation rule.",
            "No consequence received a success/failure label.",
            "No preferred communication act or state transition was supplied.",
        ],
    }
    Path(".ci").mkdir(exist_ok=True)
    Path(".ci/communication-independent-consequence.json").write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
