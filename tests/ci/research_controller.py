from cognitia.evidence.landscape import LandscapeDecision
from cognitia.research_controller import ResearchController

controller = ResearchController()
state = controller.initialize("Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?")
first = controller.next_action(state)
assert first.action == "acquire_evidence"

conflicted = LandscapeDecision(
    conclusion="conflicted",
    confidence=0.0,
    supporting_claims=("claim-a",),
    contradicting_claims=("claim-b",),
    unresolved_gaps=(),
    next_action="run a discriminating investigation against the conflicting claims",
)
state = controller.update(
    state,
    landscape=conflicted,
    answer_elements=("cause",),
    direct_answer_present=True,
    explanation_present=True,
    evidence_present=True,
)
next_action = controller.next_action(state)
assert next_action.action == "investigate"
assert next_action.terminal is False

supported = LandscapeDecision(
    conclusion="supported",
    confidence=0.91,
    supporting_claims=("claim-a",),
    contradicting_claims=(),
    unresolved_gaps=(),
    next_action="seek an independent challenge before promotion",
)
state = controller.update(state, landscape=supported)
assert controller.next_action(state).terminal is False

print("RESEARCH_CONTROLLER_SUCCESS")
