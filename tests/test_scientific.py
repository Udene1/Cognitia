import pytest

from cognitia.learning import Hypothesis, ScientificEvaluator


def test_matching_prediction_supports_hypothesis_without_changing_confidence():
    hypothesis = Hypothesis(
        proposition="force produces acceleration",
        domain="mechanics",
        confidence=0.95,
    )
    result = ScientificEvaluator().evaluate(
        predicted=10.0,
        observed=10.0,
        condition="constant_mass_and_net_force",
    )

    updated = hypothesis.with_test(result)

    assert result.verdict == "supporting"
    assert updated.status == "supported"
    assert updated.support_count == 1
    assert updated.confidence == 0.95
    assert updated.tested_conditions == ("constant_mass_and_net_force",)


def test_failed_prediction_challenges_but_does_not_destroy_hypothesis():
    hypothesis = Hypothesis(
        proposition="force produces acceleration",
        domain="mechanics",
        confidence=0.99,
    )
    result = ScientificEvaluator().evaluate(
        predicted=10.0,
        observed=7.5,
        condition="unexplained_external_influence",
    )

    updated = hypothesis.with_test(result)

    assert result.verdict == "challenging"
    assert updated.status == "challenged"
    assert updated.challenge_count == 1
    assert updated.confidence == 0.99
    assert updated.tested_conditions == ("unexplained_external_influence",)


def test_supporting_and_challenging_evidence_produce_mixed_status():
    hypothesis = Hypothesis(
        proposition="model predicts observed outcome",
        domain="test",
    )
    evaluator = ScientificEvaluator()

    updated = hypothesis.with_test(evaluator.evaluate(predicted=4, observed=4))
    updated = updated.with_test(evaluator.evaluate(predicted=4, observed=5))

    assert updated.status == "mixed"
    assert updated.support_count == 1
    assert updated.challenge_count == 1
    assert updated.confidence == 0.5


def test_invalid_verdict_and_confidence_are_rejected():
    with pytest.raises(ValueError):
        Hypothesis(proposition="x", domain="test", confidence=1.1)

    with pytest.raises(ValueError):
        ScientificEvaluator().evaluate(
            predicted=1,
            observed=1,
            reliability=1.1,
        )
