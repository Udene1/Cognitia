"""Verify that live Cognitia research terminates in an actual answer.

The benchmark deliberately performs real web acquisition. It does not embed the
historical observations used by the deterministic synthesis unit test.
"""
from cognitia.answering import AnsweringCore
from cognitia.open_research import OpenEndedResearch
from cognitia.research_synthesis import ResearchSynthesisEngine


QUESTION = "Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?"


def main() -> None:
    result = OpenEndedResearch().investigate(
        QUESTION,
        max_rounds=4,
        search_results=5,
        documents_per_round=3,
        claims_per_document=12,
    )
    synthesis = ResearchSynthesisEngine().synthesize(result)
    answer = AnsweringCore().build(synthesis)

    assert result.rounds, "live research produced no rounds"
    assert result.claims, "live research produced no candidate claims"
    assert answer.answer.strip(), "answering core returned an empty answer"
    assert answer.sufficient, answer.assessment
    assert "best current explanation" in answer.answer.lower() or "best current answer" in answer.answer.lower()
    assert answer.epistemic.verification_required
    assert answer.research_status == synthesis.status

    print("LIVE_OPEN_ENDED_ANSWER_SUCCESS")
    print(f"ROUNDS={len(result.rounds)}")
    print(f"CLAIMS={len(result.claims)}")
    print(f"SYNTHESIS_STATUS={synthesis.status}")
    print(f"ANSWER_CONFIDENCE={answer.epistemic.confidence}")
    print("ANSWER")
    print(answer.render())


if __name__ == "__main__":
    main()
