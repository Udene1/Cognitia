"""Capability-level checks for Cognitia's language representation boundary."""
from cognitia.language import analyze_question, build_language_frame


def main() -> None:
    frame = build_language_frame(
        "Political instability weakened the Roman Empire in 476 because repeated civil conflict reduced central control."
    )
    assert frame.tokens
    assert frame.entities
    assert frame.relations
    assert any(relation.predicate == "weakened" for relation in frame.relations)
    assert "476" in frame.temporal_markers
    assert frame.relations[0].confidence == "candidate"
    assert frame.propositions
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

    why = analyze_question("Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?")
    assert why.question_type == "explanation_or_cause"
    assert why.contract.needs_explanation
    assert why.contract.needs_evidence
    assert "causal explanation" in why.contract.required_elements
    assert "supporting evidence" in why.contract.required_elements
    assert "compare_explanations" in why.requested_operations

    why_short = analyze_question("Why did the Roman Empire decline?")
    assert why_short.question_type == "explanation_or_cause"
    assert why_short.contract.needs_explanation
    assert not why_short.contract.needs_evidence

    how = analyze_question("How does photosynthesis work?")
    assert how.question_type == "procedure_or_mechanism"
    assert how.contract.needs_explanation
    assert "process or mechanism" in how.contract.required_elements

    when = analyze_question("When was the kilogram redefined?")
    assert when.question_type == "time_or_event"
    assert when.contract.requested_length == "short"

    what = analyze_question("What is photosynthesis?")
    assert what.question_type == "definition_or_fact"
    assert what.contract.answer_kind == "definition_or_fact"

    print("LANGUAGE_REPRESENTATION_SUCCESS")
    print(f"tokens={len(frame.tokens)} entities={len(frame.entities)} relations={len(frame.relations)}")
    print(f"why_contract={why.contract}")


if __name__ == "__main__":
    main()
