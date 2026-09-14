"""Capability proof: structural analogy is retrieved, adapted, then verified."""
from cognitia.language import build_language_frame
from cognitia.structural_transfer import StructuralSignature, StructuralTransferEngine, signature_from_language
from cognitia.answer_plan import AnswerSufficiencyEvaluator
from cognitia.language import analyze_question


def main() -> None:
    source = signature_from_language(build_language_frame("Political instability weakened the Roman Empire."))
    target = signature_from_language(build_language_frame("A governance failure weakened the organization."))
    engine = StructuralTransferEngine()
    candidates = engine.retrieve(target, (source,))
    assert candidates
    candidate = candidates[0]
    assert candidate.status == "candidate"
    assert candidate.similarity > 0

    verification = engine.verify(
        candidate,
        adapter=lambda item: {"shared": item.shared_structure, "target": item.target.outcome_shape},
        verifier=lambda adapted: bool(adapted["shared"]),
    )
    assert verification.adapted
    assert verification.verified
    assert verification.status == "validated_transfer"

    why = analyze_question("Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?")
    plan = AnswerSufficiencyEvaluator().evaluate(
        why.contract,
        elements=("causal explanation", "supporting evidence or reasoning", "uncertainty where applicable"),
        evidence_count=3,
        uncertainty_explicit=True,
        unresolved_gaps=1,
    )
    assert plan.sufficient
    assert not plan.needs_more_investigation

    simple = analyze_question("Is water liquid at room temperature?")
    direct = AnswerSufficiencyEvaluator().evaluate(simple.contract, elements=("direct answer",))
    assert direct.sufficient
    assert direct.rationale == "answer contract satisfied"

    print("STRUCTURAL_TRANSFER_AND_ANSWER_PLANNING_SUCCESS")
    print(f"similarity={candidate.similarity:.3f} shared={candidate.shared_structure}")
    print(f"why_plan={plan}")


if __name__ == "__main__":
    main()
