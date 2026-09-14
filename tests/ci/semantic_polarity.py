"""Polarity must survive the semantic -> cognitive boundary."""
from cognitia.language import analyze_question, build_language_frame


def main() -> None:
    negative = build_language_frame("The evidence does not establish that the reform caused the decline.")
    assert negative.semantic_propositions[0].polarity == "negative"
    assert negative.relations
    assert all(relation.polarity == "negative" for relation in negative.relations)

    uncertain = build_language_frame("The reform may have changed the definition in 2019.")
    assert uncertain.semantic_propositions[0].modality == "uncertain"
    assert uncertain.semantic_propositions[0].confidence == "candidate_uncertain"

    analysis = analyze_question("Why did the Roman Empire decline?")
    assert analysis.cognitive is not None
    assert analysis.cognitive.semantic_propositions
    assert analysis.cognitive.semantic_propositions[0].confidence == "candidate"
    assert any(goal.operation == "construct_explanation" for goal in analysis.cognitive.goals)

    print("SEMANTIC_POLARITY_COGNITION_SUCCESS")
    print(f"relations={len(negative.relations)} cognitive_relations={len(analysis.cognitive.relations)}")


if __name__ == "__main__":
    main()
