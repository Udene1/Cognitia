from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ObservedConsequence
from cognitia.experience_state import ClaimSource, apply_experience_to_state

state = CognitiveState(problem="new problem", knowledge_ids=("knowledge:independent",))
experience = Experience(experience_id="exp-refuted-check", prior_state=state, action="inspect", rationale="Relevant prior observation", expected=ExpectedConsequence("success"), observed=ObservedConsequence("failure", EpistemicOutcome.REFUTED), state_update=state, provenance=("direct-observation",))
result = apply_experience_to_state(state, experience)
assert result.changed
assert result.source is ClaimSource.UNCERTAINTY
assert result.resulting_state.knowledge_ids == state.knowledge_ids
assert "refuted-experience:exp-refuted-check" in result.resulting_state.uncertainty
assert result.requires_epistemic_test
assert not result.epistemically_established
print("PASS")
