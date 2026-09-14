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
    assert frame.semantic_propositions
    assert frame.semantic_propositions[0].confidence == "candidate"

    uncertain = build_language_frame("The reform may have changed the definition in 2019.")
    assert uncertain.modality == ("may",)
    assert uncertain.semantic_propositions[0].modality == "uncertain"
    assert uncertain.semantic_propositions[0].confidence == "candidate_uncertain"
    assert uncertain.relations[0].modality == "uncertain"

    negative = build_language_frame("The evidence does not establish that the reform caused the decline.")
    assert negative.negation_markers == ("does not",)
    assert negative.negated
    assert negative.semantic_propositions[0].polarity == "negative"

    yes_no = analyze_question("Is the Roman Empire's decline caused by one factor?")
    assert yes_no.question_type == "yes_no"
    assert yes_no.contract.answer_kind == "yes_no"
    assert yes_no.contract.requested_length == "short_with_justification"
    assert yes_no.contract.needs_explanation
    assert yes_no.contract.needs_evidence
    assert not yes_no.contract.bare_answer_sufficient
    assert yes_no.frame.answer_contract == yes_no.contract

    simple_yes_no = analyze_question("Is water liquid at room temperature?")
    assert simple_yes_no.question_type == "yes_no"
    assert simple_yes_no.contract.requested_length == "short"
    assert simple_yes_no.contract.bare_answer_sufficient

    why = analyze_question("Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?")
    assert why.question_type == "explanation_or_cause"
    assert why.contract.needs_explanation
    assert why.contract.needs_evidence
    assert why.contract.needs_uncertainty
    assert "causal explanation" in why.contract.required_elements
    assert "supporting evidence or reasoning" in why.contract.required_elements
    assert "state unresolved explanatory gaps" in why.contract.stopping_conditions

    how = analyze_question("How does photosynthesis work?")
    assert how.question_type == "procedure_or_mechanism"
    assert how.contract.needs_explanation
    assert not how.contract.bare_answer_sufficient
    assert "mechanism or ordered procedure" in how.contract.required_elements

    when = analyze_question("When was the kilogram redefined?")
    assert when.question_type == "time_or_event"
    assert when.contract.requested_length == "short"
    assert when.contract.bare_answer_sufficient

    what = analyze_question("What is photosynthesis?")
    assert what.question_type == "fact_or_identification"
    assert what.contract.answer_kind == "fact_or_identification"

    print("LANGUAGE_REPRESENTATION_SUCCESS")
    print(f"tokens={len(frame.tokens)} entities={len(frame.entities)} relations={len(frame.relations)}")
    print(f"why_contract={why.contract}")


if __name__ == "__main__":
    main()
