"""Protocol-level tests for experience-conditioned research.

These tests intentionally verify invariants, not expected cognitive answers.
They prevent the experiment from silently turning experience into an
unconditional routing rule.
"""

from cognitia.experience import (
    CognitiveState,
    EpistemicOutcome,
    ExpectedConsequence,
    Experience,
    ExperienceLedger,
    ObservedConsequence,
)


def episode(experience_id: str, *, evidence=("e1",), outcome=EpistemicOutcome.CONFIRMED):
    prior = CognitiveState(
        "new problem",
        evidence_ids=tuple(evidence),
        hypothesis_ids=("h1",),
        uncertainty=("u1",),
        goal="explain",
    )
    updated = CognitiveState(
        "new problem",
        evidence_ids=tuple(evidence) + ("e2",),
        hypothesis_ids=("h1",),
        uncertainty=(),
        goal="explain",
    )
    return Experience(
        experience_id=experience_id,
        prior_state=prior,
        action="investigate",
        rationale="The available state does not resolve the question.",
        expected=ExpectedConsequence("the next observation resolves the uncertainty"),
        observed=ObservedConsequence(
            "the next observation resolves the uncertainty",
            outcome,
            ("e2",),
        ),
        state_update=updated,
        provenance=("experience-blindspot-protocol",),
    )


def test_experience_marks_epistemic_refutation_as_discrepancy():
    item = episode("x1", outcome=EpistemicOutcome.REFUTED)
    assert item.expected.description != ""
    assert item.observed.outcome is EpistemicOutcome.REFUTED
    assert item.discrepancy is True


def test_conflicting_outcome_remains_available_to_future_reasoning():
    item = episode("x2", outcome=EpistemicOutcome.REFUTED)
    ledger = ExperienceLedger((item,))
    assert ledger.by_outcome(EpistemicOutcome.REFUTED) == (item,)
    assert ledger.by_outcome(EpistemicOutcome.CONFIRMED) == ()


def test_relevant_experience_is_retrieved_by_state_links_not_by_answer_label():
    item = episode("x3", evidence=("database-unavailable",))
    ledger = ExperienceLedger((item,))
    assert ledger.relevant_to(evidence_ids=("database-unavailable",)) == (item,)
    assert ledger.relevant_to(evidence_ids=("different-domain",)) == ()


def test_multiple_experiences_can_coexist_without_overwriting_history():
    first = episode("x4", evidence=("e1",))
    second = episode("x5", evidence=("e9",), outcome=EpistemicOutcome.REFUTED)
    ledger = ExperienceLedger((first, second))
    assert [item.experience_id for item in ledger.all()] == ["x4", "x5"]
