from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ObservedConsequence
from cognitia.experience_state import ClaimSource, apply_experience_to_state

state = CognitiveState(problem="new structurally related problem", knowledge_ids=("knowledge:independent",), uncertainty=("uncertain:new",))
experience = Experience(experience_id="exp-check", prior_state=state, action="inspect", rationale="Relevant prior observation", expected=ExpectedConsequence("success"), observed=ObservedConsequence("success", EpistemicOutcome.CONFIRMED), state_update=state, provenance=("direct-observation",))
result = apply_experience_to_state(state, experience)
assert result.changed
assert result.source is ClaimSource.EXPERIENCE
assert result.resulting_state.knowledge_ids == state.knowledge_ids
assert "experience:exp-check" in result.resulting_state.hypothesis_ids
assert result.requires_epistemic_test
assert not result.epistemically_established
print("PASS")
