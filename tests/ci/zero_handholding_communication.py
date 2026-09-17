from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from cognitia.answering import AnsweringCore
from cognitia.research_synthesis import FactorExplanation, ResearchSynthesis


@dataclass(frozen=True)
class InteractionContext:
    objective: str
    recipient: str


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
    contexts = (
        InteractionContext("inform", "operator"),
        InteractionContext("teach", "learner"),
        InteractionContext("decide", "decision_maker"),
        InteractionContext("coordinate", "operator"),
    )

    outputs = []
    for context in contexts:
        answer = core.build(synthesis)
        outputs.append(
            {
                "context": {"objective": context.objective, "recipient": context.recipient},
                "answer": answer.answer,
                "reasoning": answer.reasoning,
                "evidence": answer.evidence,
                "uncertainty": answer.uncertainty,
                "limitations": answer.limitations,
                "verification_actions": answer.verification_actions,
                "epistemic": {
                    "status": answer.epistemic.status,
                    "confidence": answer.epistemic.confidence,
                    "verification_required": answer.epistemic.verification_required,
                },
            }
        )

    communication_payloads = [
        json.dumps({key: value for key, value in item.items() if key != "context"}, sort_keys=True)
        for item in outputs
    ]
    distinct_communication_outputs = len(set(communication_payloads))
    artifact = {
        "experiment": "zero_handholding_communication_exposure",
        "question": "Does the current communication-facing answering core change its output when the same cognitive state is exposed under different objectives and recipients?",
        "handholding": {
            "expected_communication_strategy": None,
            "expected_winner": None,
            "researcher_selected_act": None,
            "consequence_interpretation": None,
        },
        "contexts": [item["context"] for item in outputs],
        "distinct_communication_outputs": distinct_communication_outputs,
        "communication_outputs_identical": distinct_communication_outputs == 1,
        "observations": [
            "The same ResearchSynthesis was supplied for every interaction.",
            "Objective and recipient were recorded as interaction context but were not injected into AnsweringCore as instructions or expected behavior.",
            "No communication policy, act mapping, or adaptation mechanism was added by this experiment.",
        ],
        "results": outputs,
        "interpretation": (
            "The current answering path produced identical communication content and epistemic fields across the exposed contexts. "
            "This is an observed capability boundary, not a failure patched by the experiment."
            if distinct_communication_outputs == 1
            else "The current answering path produced different communication content or epistemic fields across the exposed contexts; inspect the differences before adding communication machinery."
        ),
    }

    path = Path(".ci/zero-handholding-communication-exposure.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
