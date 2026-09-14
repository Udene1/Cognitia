"""Prove research actions are selected from the current evidence state."""
from cognitia.document_claims import ExtractedClaim
from cognitia.research_autonomy import ResearchActionController


def claim(text: str) -> ExtractedClaim:
    return ExtractedClaim(
        id=text[:12],
        proposition=text,
        observation_id="obs",
        source="source",
        sentence=text,
        confidence=0.7,
        temporal_markers=(),
        entities=(),
        relations=(),
        uncertainty_markers=(),
    )


def main() -> None:
    controller = ResearchActionController()
    question = "Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?"

    first = controller.choose(question, unresolved=("need independent evidence",))
    assert first is not None
    assert first.action.query.objective == question

    second = controller.choose(
        question,
        claims=(
            claim("The Western Roman Empire declined because of internal political instability."),
            claim("The Western Roman Empire did not decline because of internal political instability."),
        ),
        observed_queries=(first.action.query.objective,),
        unresolved=("competing explanations remain unresolved",),
    )
    assert second is not None
    assert second.action.query.objective != first.action.query.objective
    assert second.action.purpose in {"independent check", "contradiction resolution"}
    assert second.expected_information_gain > 0
    assert "competing evidence" in second.rationale

    print("RESEARCH_ACTION_CONTROL_SUCCESS")
    print(f"FIRST={first.action.query.objective}")
    print(f"SECOND={second.action.query.objective}")
    print(f"SECOND_PURPOSE={second.action.purpose}")
    print(f"RATIONALE={second.rationale}")


if __name__ == "__main__":
    main()
