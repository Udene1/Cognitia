from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from cognitia.answering import AnsweringCore
from cognitia.research_synthesis import FactorExplanation, ResearchSynthesis


@dataclass(frozen=True)
class Recipient:
    name: str
    follow_up: str

    def receive(self, message: str) -> str:
        # The recipient owns the consequence. Cognitia is not told whether its
        # message was effective and is not given a target response.
        return self.follow_up


def _state() -> ResearchSynthesis:
    return ResearchSynthesis(
        question="Why did service X fail?",
        status="candidate_multi_factor_synthesis",
        thesis="The available evidence supports multiple candidate contributors, but does not establish one explanation.",
        factors=(
            FactorExplanation("resource exhaustion", "resource exhaustion contributed to the failure", ("C1",), 1, 1, "candidate", "systemic", ("O1",)),
            FactorExplanation("dependency failure", "dependency failure contributed to the failure", ("C2",), 1, 1, "candidate_uncertain", "systemic", ("O2",)),
        ),
        complementary_domains=("systemic",),
        competing_explanations=(),
        distinguishing_evidence=("a trace separating resource exhaustion from dependency failure",),
        caveats=("The current evidence does not establish the relative importance of the candidates.",),
        next_actions=("Acquire the discriminating trace.",),
    )


def main() -> None:
    synthesis = _state()
    core = AnsweringCore()
    recipients = (
        Recipient("operator", "I received the report. What should I inspect next?"),
        Recipient("learner", "I received the explanation. What does the uncertainty mean?"),
        Recipient("decision_maker", "I received the report. What decision is justified now?"),
    )

    interactions = []
    for recipient in recipients:
        before = core.build(synthesis)
        message = before.render()
        consequence = recipient.receive(message)
        # No learning rule or expected adaptation is supplied. We only expose
        # the consequence to the existing revision boundary and observe whether
        # the current synthesis actually changes.
        after, revision = core.revise(before, synthesis, new_evidence=(consequence,))
        interactions.append(
            {
                "recipient": recipient.name,
                "message": message,
                "consequence": consequence,
                "before_fingerprint": revision.previous_fingerprint,
                "after_fingerprint": revision.new_fingerprint,
                "cognitive_state_changed": revision.changed,
                "changed_because": revision.changed_because,
                "after_answer": after.answer,
                "after_epistemic": {
                    "status": after.epistemic.status,
                    "confidence": after.epistemic.confidence,
                    "verification_required": after.epistemic.verification_required,
                },
            }
        )

    artifact = {
        "experiment": "communication_consequence_exposure",
        "question": "After Cognitia communicates and receives an actual recipient consequence, does the existing cognitive state change without a supplied communication-learning rule?",
        "handholding": {
            "expected_communication_strategy": None,
            "expected_effective_message": None,
            "expected_consequence": None,
            "learning_rule": None,
            "expected_state_change": None,
        },
        "observations": [
            "Recipients generate their own follow-up consequence independently of a communication score or success label.",
            "Cognitia's message is not modified before the recipient receives it.",
            "The recipient consequence is passed through the existing answer revision boundary as new evidence.",
            "No rule maps a consequence to a preferred communication act or state transition.",
        ],
        "cognitive_state_changed_for_all": all(item["cognitive_state_changed"] for item in interactions),
        "interactions": interactions,
        "interpretation": (
            "The consequence reached the existing revision boundary, but the current cognitive state did not change in response to any recipient consequence. "
            "This is an observed boundary: consequence exposure exists, but consequence-driven cognitive change is not yet demonstrated."
            if not any(item["cognitive_state_changed"] for item in interactions)
            else "At least one recipient consequence changed the current cognitive state. Inspect the exact change before introducing any learning abstraction."
        ),
    }
    path = Path(".ci/communication-consequence-exposure.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
