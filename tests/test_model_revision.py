from cognitia.learning.model_revision import RevisionAction, RevisionDecision, revise_hypothesis
from cognitia.learning.scientific import Hypothesis, TestResult


def test_revision_keeps_evidence_and_explicitly_changes_confidence():
    hypothesis = Hypothesis("gravity model predicts 9.8", "mechanics", confidence=0.9)
    result = TestResult("challenging", 9.8, 10.7, condition="trial-1")

    revised = revise_hypothesis(
        hypothesis,
        result,
        decision=RevisionDecision(
            RevisionAction.DOWNGRADE,
            "Observed discrepancy exceeds the declared experimental bound.",
            revised_confidence=0.7,
        ),
    )

    assert revised.challenge_count == 1
    assert revised.tested_conditions == ("trial-1",)
    assert revised.confidence == 0.7


def test_revision_without_confidence_policy_does_not_guess():
    hypothesis = Hypothesis("model", "test", confidence=0.8)
    result = TestResult("challenging", 1, 2)

    revised = revise_hypothesis(
        hypothesis,
        result,
        decision=RevisionDecision(RevisionAction.CHALLENGE, "Challenge recorded; more evidence required."),
    )

    assert revised.confidence == 0.8
    assert revised.challenge_count == 1
