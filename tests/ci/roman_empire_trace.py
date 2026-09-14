"""End-to-end Roman Empire cognition trace with real evidence revision.

No political, military, or economic factor is seeded here. Cognitia must acquire
claims from the live research environment, form its own hypotheses, synthesize,
answer, and then incorporate a separately acquired challenge episode.
"""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.answering import AnsweringCore
from cognitia.open_research import OpenEndedResearch
from cognitia.research_synthesis import ResearchSynthesisEngine
from cognitia.research_trace import ResearchTrace

QUESTION = "Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?"
CHALLENGE = "Roman Empire decline climate disease demographic evidence challenges traditional explanations"


def main() -> None:
    research = OpenEndedResearch()
    first = research.investigate(QUESTION, max_rounds=4, search_results=5, documents_per_round=3, claims_per_document=20)
    synthesis_engine = ResearchSynthesisEngine()
    answering = AnsweringCore()

    first_synthesis = synthesis_engine.synthesize(first)
    first_answer = answering.build(first_synthesis)
    first_trace = ResearchTrace.build(first, first_synthesis, first_answer)

    assert first.rounds, "Cognition did not choose any searches"
    assert first.claims, "Cognition acquired no candidate claims"
    assert first_answer.answer, "Cognition produced no answer"
    assert first_trace.search_plan and first_trace.evidence_acquired
    assert first_trace.claims_formed and first_trace.hypotheses_considered

    # Acquire a genuinely new research episode aimed at challenging the first
    # landscape. Nothing about the expected factor list is supplied to Cognitia.
    challenge = research.investigate(CHALLENGE, max_rounds=3, search_results=5, documents_per_round=3, claims_per_document=20)
    combined = first.augment(challenge)
    combined_synthesis = synthesis_engine.synthesize(combined)
    second_answer, revision = answering.revise(
        first_answer,
        combined_synthesis,
        new_evidence=tuple(claim.proposition for claim in challenge.claims),
    )
    second_trace = ResearchTrace.build(combined, combined_synthesis, second_answer, revision=revision)

    assert challenge.rounds, "Challenge episode did not choose searches"
    assert challenge.claims, "Challenge episode acquired no claims"
    assert revision.changed, "New evidence did not change the candidate answer"
    assert revision.previous_fingerprint != revision.new_fingerprint
    assert second_trace.revision is not None
    assert len(second_trace.search_plan) > len(first_trace.search_plan)
    assert len(second_trace.claims_formed) >= len(first_trace.claims_formed)

    output = {
        "initial": first_trace.to_dict(),
        "updated": second_trace.to_dict(),
        "revision": revision.__dict__,
    }
    Path(".ci").mkdir(exist_ok=True)
    Path(".ci/roman-empire-trace.json").write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")

    print("ROMAN_EMPIRE_TRACE_SUCCESS")
    print(f"INITIAL_ROUNDS={len(first.rounds)}")
    print(f"INITIAL_CLAIMS={len(first.claims)}")
    print(f"INITIAL_HYPOTHESES={len(first_trace.hypotheses_considered)}")
    print(f"INITIAL_CONFIDENCE={first_answer.epistemic.confidence}")
    print(f"CHALLENGE_ROUNDS={len(challenge.rounds)}")
    print(f"NEW_CLAIMS={len(challenge.claims)}")
    print(f"UPDATED_HYPOTHESES={len(second_trace.hypotheses_considered)}")
    print(f"UPDATED_CONFIDENCE={second_answer.epistemic.confidence}")
    print(f"REVISION_CHANGED={revision.changed}")
    print("INITIAL_ANSWER=")
    print(first_answer.render())
    print("\nUPDATED_ANSWER=")
    print(second_answer.render())


if __name__ == "__main__":
    main()
