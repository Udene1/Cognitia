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

    yes_no = analyze_question("Is the Roman Empire's decline caused by one factor?")
    assert yes_no.question_type == "yes_no"
    assert yes_no.contract.answer_kind == "yes_no"
    assert yes_no.contract.requested_length == "short"

    why = analyze_question("Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?")
    assert why.question_type == "explanation_or_cause"
    assert why.contract.needs_explanation
    assert why.contract.needs_evidence
    assert "causal explanation" in why.contract.required_elements

    how = analyze_question("How does photosynthesis work?")
    assert how.question_type == "procedure_or_mechanism"
    assert how.contract.needs_explanation

    when = analyze_question("When was the kilogram redefined?")
    assert when.question_type == "time_or_event"
    assert when.contract.requested_length == "short"

    print("LANGUAGE_REPRESENTATION_SUCCESS")


if __name__ == "__main__":
    main()
