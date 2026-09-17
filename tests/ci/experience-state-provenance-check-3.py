from cognitia.experience import CognitiveState, EpistemicOutcome, ExpectedConsequence, Experience, ObservedConsequence
from cognitia.experience_state import apply_experience_to_state

state = CognitiveState(problem="new problem", knowledge_ids=("knowledge:independent",))
experience = Experience(experience_id="exp-knowledge-isolation", prior_state=state, action="inspect", rationale="Relevant observation", expected=ExpectedConsequence("success"), observed=ObservedConsequence("success", EpistemicOutcome.CONFIRMED), state_update=state, provenance=("observation",))
result = apply_experience_to_state(state, experience)
assert result.resulting_state.knowledge_ids == ("knowledge:independent",)
assert result.resulting_state.hypothesis_ids == ("experience:exp-knowledge-isolation",)
print("PASS")
