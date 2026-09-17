from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ObservedConsequence
from cognitia.experience_state import ClaimSource, apply_experience_to_state

base = CognitiveState(problem="novel problem", knowledge_ids=("k1",), uncertainty=("u1",))
exp = Experience(
    experience_id="exp-provenance",
    prior_state=base,
    action="inspect",
    rationale="Relevant prior experience",
    expected=ExpectedConsequence("works"),
    observed=ObservedConsequence("works", EpistemicOutcome.CONFIRMED),
    state_update=base,
    provenance=("observation",),
)
transition = apply_experience_to_state(base, exp)
assert transition.changed
assert transition.source is ClaimSource.EXPERIENCE
assert transition.resulting_state.knowledge_ids == base.knowledge_ids
assert "experience:exp-provenance" in transition.resulting_state.hypothesis_ids
assert transition.requires_epistemic_test
assert not transition.epistemically_established
print("experience-state-provenance smoke test: PASS")
