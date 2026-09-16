from cognitia.experience import (
    CognitiveState,
    EpistemicOutcome,
    ExpectedConsequence,
    Experience,
    ExperienceLedger,
    ObservedConsequence,
)


def make_experience(experience_id: str, action: str = "investigate") -> Experience:
    prior = CognitiveState("explain failure", evidence_ids=("e1",), hypothesis_ids=("h1",), goal="explain")
    return Experience(
        experience_id=experience_id,
        prior_state=prior,
        action=action,
        rationale="Current evidence is insufficient.",
        expected=ExpectedConsequence("new evidence resolves the cause"),
        observed=ObservedConsequence("new evidence resolves the cause", EpistemicOutcome.CONFIRMED, ("e2",)),
        state_update=CognitiveState("explain failure", evidence_ids=("e1", "e2"), hypothesis_ids=("h1",), goal="explain"),
        provenance=("test",),
    )


def test_experience_ledger_retains_causal_episode():
    experience = make_experience("e-1")
    ledger = ExperienceLedger((experience,))
    assert ledger.all() == (experience,)
    assert ledger.relevant_to(evidence_ids=("e1",)) == (experience,)


def test_experience_duplicate_ids_are_not_overwritten():
    experience = make_experience("e-1")
    ledger = ExperienceLedger((experience,))
    try:
        ledger.record(experience)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate experience ID was silently overwritten")
