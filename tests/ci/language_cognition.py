"""Capability proof for language semantics and answer-contract reasoning."""
from cognitia.answer_contract import AnswerContractPlanner
from cognitia.language import analyze_question, build_language_frame


def main() -> None:
    frame = build_language_frame(
        "According to historians, political instability weakened the Roman Empire in 476 because repeated civil conflict reduced central control."
    )
    assert frame.tokens
    assert frame.entities
    assert frame.relations
    assert frame.events
    assert frame.causal_relations
    assert frame.temporal_markers == ("in", "476")
    assert frame.attribution_markers
    assert frame.propositions[0].attribution is not None
    assert frame.propositions[0].confidence == "candidate"

    uncertain = build_language_frame("The reform may have changed the definition in 2019.")
    assert uncertain.modality_markers == ("may",)
    assert uncertain.propositions[0].modality == "uncertain"
    assert uncertain.propositions[0].confidence == "candidate_uncertain"

    negative = build_language_frame("The evidence does not establish that the reform caused the decline.")
    assert negative.negation_markers == ("does not",)
    assert negative.propositions[0].polarity == "negative"

    yes_no = analyze_question("Is the Roman Empire's decline caused by one factor?")
    assert yes_no.question_type == "yes_no"
    assert yes_no.contract.answer_kind == "yes_no"
    assert yes_no.contract.requested_length == "short"
    assert not yes_no.contract.needs_explanation
    assert yes_no.requested_operations == ("classify_proposition",)

    why = analyze_question("Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?")
    assert why.question_type == "explanation_or_cause"
    assert why.contract.needs_explanation
    assert why.contract.needs_evidence
    assert "causal explanation" in why.contract.required_elements
    assert "supporting evidence" in why.contract.required_elements
    assert "compare_explanations" in why.requested_operations
    assert "satisfy_all_subquestions" in why.requested_operations
    assert len(why.subquestions) >= 2

    short_why = analyze_question("Why did the Roman Empire decline?")
    assert short_why.contract.needs_explanation
    assert not short_why.contract.needs_evidence

    how = analyze_question("How does photosynthesis work?")
    assert how.contract.needs_explanation
    assert "process or mechanism" in how.contract.required_elements

    plan = AnswerContractPlanner().plan(why)
    assert plan.needs_evidence
    assert "direct_answer" in plan.sections
    assert "explanation" in plan.sections
    assert "evidence" in plan.sections

    sufficient = AnswerContractPlanner().assess(
        why.contract,
        elements=("causal explanation", "contribution or mechanism", "supporting evidence", "contradicting or distinguishing evidence", "uncertainty"),
        direct_answer=True,
        explanation=True,
        evidence=True,
    )
    assert sufficient.sufficient

    insufficient = AnswerContractPlanner().assess(why.contract, elements=("causal explanation",), direct_answer=True, explanation=True)
    assert not insufficient.sufficient
    assert "supporting evidence" in insufficient.missing_elements

    print("LANGUAGE_COGNITION_SUCCESS")
    print(f"semantic_relations={len(frame.relations)} causal_relations={len(frame.causal_relations)} events={len(frame.events)}")
    print(f"answer_plan={plan}")


if __name__ == "__main__":
    main()
