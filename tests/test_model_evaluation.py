from cognitia.physics.measurement import Measurement, Uncertainty, compare_prediction
from cognitia.physics.model_evaluation import ModelEvidence, evaluate_prediction


def test_prediction_within_uncertainty_is_supporting_evidence():
    error = compare_prediction(
        10.2,
        Measurement(10.0, Uncertainty(0.3)),
        model="test_model",
    )
    evaluation = evaluate_prediction(error, condition="controlled")

    assert evaluation.evidence is ModelEvidence.SUPPORTING
    assert evaluation.condition == "controlled"


def test_prediction_outside_bound_is_challenging_without_claiming_falsity():
    error = compare_prediction(
        11.0,
        Measurement(10.0, Uncertainty(0.2)),
        model="test_model",
    )
    evaluation = evaluate_prediction(error)

    assert evaluation.evidence is ModelEvidence.CHALLENGING
    assert "investigate" in evaluation.reason
