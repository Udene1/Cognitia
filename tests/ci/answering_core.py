from cognitia.answering import AnsweringCore
from cognitia.research_synthesis import FactorExplanation, ResearchSynthesis


def _synthesis(question: str, *, factors: tuple[FactorExplanation, ...], status: str = "candidate_multi_factor_synthesis") -> ResearchSynthesis:
    domains = tuple(dict.fromkeys(f.domain for f in factors))
    return ResearchSynthesis(
        question=question,
        status=status,
        thesis="candidate synthesis",
        factors=factors,
        complementary_domains=domains,
        competing_explanations=(),
        distinguishing_evidence=("independent verification", "mechanism and timing check"),
        caveats=("Finding count is not independent-source count.",),
        next_actions=("Acquire independent evidence.", "Test the mechanism."),
    )


def main() -> None:
    factors = (
        FactorExplanation(
            factor="political instability and civil conflict weakened governance",
            contribution="Political instability weakened the Roman Empire through repeated civil conflict.",
            claim_ids=("c1",), source_count=1, origin_count=1, confidence="candidate", domain="political",
        ),
        FactorExplanation(
            factor="frontier pressure weakened armed forces",
            contribution="Frontier pressure contributed by weakening armed forces.",
            claim_ids=("c2",), source_count=1, origin_count=1, confidence="candidate", domain="military",
        ),
        FactorExplanation(
            factor="fiscal strain reduced reliable tax revenue",
            contribution="Fiscal strain contributed because tax revenue became less reliable.",
            claim_ids=("c3",), source_count=1, origin_count=1, confidence="candidate", domain="economic",
        ),
    )
    core = AnsweringCore()
    first = core.build(_synthesis("Why did the Roman Empire decline?", factors=factors))

    assert first.sufficient, first.assessment
    assert first.epistemic.verification_required
    assert first.answer.startswith("Why did the Roman Empire decline?")
    assert "political instability" in first.answer
    assert "frontier pressure" in first.answer
    assert "fiscal strain" in first.answer
    assert first.uncertainty
    assert "Verification:" in first.render()

    revised_factors = (
        factors[0],
        FactorExplanation(
            factor="fiscal strain was severe enough to reduce state capacity",
            contribution="New independent evidence indicates fiscal strain materially reduced state capacity.",
            claim_ids=("c3", "c4"), source_count=2, origin_count=2, confidence="candidate", domain="economic",
        ),
    )
    revised_synthesis = _synthesis("Why did the Roman Empire decline?", factors=revised_factors)
    second, revision = core.revise(first, revised_synthesis, new_evidence=("independent fiscal evidence",))
    assert revision.changed
    assert revision.previous_fingerprint != revision.new_fingerprint
    assert "new synthesis changed the candidate conclusion" in revision.changed_because
    assert second.sufficient

    # Capability limits constrain confidence but must not turn cognition into a refusal.
    bounded = core.build(
        _synthesis("Why did the Roman Empire decline?", factors=factors),
        capability_limits=("primary-source verification",),
    )
    assert bounded.answer
    assert "primary-source verification" in bounded.epistemic.capability_limits
    assert bounded.epistemic.verification_required

    # No evidence still produces an explicit bounded answer rather than an empty response.
    empty = core.build(
        _synthesis("What caused X?", factors=(), status="insufficient_explanatory_structure")
    )
    assert empty.answer
    assert not empty.sufficient
    assert empty.epistemic.confidence == "very_low"

    print("ANSWERING_CORE_SUCCESS")
    print(f"FIRST_CONFIDENCE={first.epistemic.confidence}")
    print(f"FIRST_SUFFICIENT={first.sufficient}")
    print(f"REVISION_CHANGED={revision.changed}")
    print(f"BOUNDED_CAPABILITY={bounded.epistemic.capability_limits}")
    print(f"EMPTY_CONFIDENCE={empty.epistemic.confidence}")
    print(first.render())


if __name__ == "__main__":
    main()
