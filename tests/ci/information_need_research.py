"""Research experiment: external search should be a conditional operation.

The experiment does not claim that keyword rules understand requests. It
records whether the explicit detector distinguishes freshness-driven external
evidence from computation and states that already contain sufficient evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.experience import CognitiveState
from cognitia.information_need import InformationNeedDetector

STATES = (
    ("fresh_external", CognitiveState("What is the latest inflation rate in Nigeria?")),
    ("computation", CognitiveState("Calculate 17 * 23.")),
    ("evidence_sufficient", CognitiveState(
        "What is 2 + 2?", evidence_ids=("arithmetic-rule",)
    )),
    ("unresolved", CognitiveState(
        "Why did the process fail?", uncertainty=("cause",)
    )),
)


def main() -> None:
    detector = InformationNeedDetector()
    records = []
    for label, state in STATES:
        need = detector.detect(state)
        records.append({
            "condition": label,
            "problem": state.problem,
            "kind": need.kind.value,
            "reasons": list(need.reasons),
            "confidence": need.confidence,
        })

    by_label = {record["condition"]: record for record in records}
    artifact = {
        "experiment": "information-need-v1",
        "research_question": "Can Cognitia make external search conditional rather than treating every request as a search task?",
        "records": records,
        "observations": {
            "freshness_requests_require_external_evidence": by_label["fresh_external"]["kind"] == "external_evidence",
            "computation_does_not_require_external_evidence": by_label["computation"]["kind"] != "external_evidence",
            "evidence_sufficient_state_does_not_require_external_evidence": by_label["evidence_sufficient"]["kind"] == "none",
            "unresolved_state_remains_unresolved": by_label["unresolved"]["kind"] == "unresolved",
        },
        "boundary": "This is a deterministic routing hypothesis, not semantic understanding. It does not establish that Cognitia knows when search is necessary in arbitrary requests.",
        "next_step": "Remove direct lexical routing as the sole discriminator and test whether action generation plus observed consequences can learn when external evidence changes the state enough to justify its cost.",
    }
    output = Path(".ci/information-need-research.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
