from cognitia.physics.measurement import (
    Measurement,
    PredictionVerdict,
    Uncertainty,
    compare_prediction,
)


def test_prediction_agrees_within_measurement_uncertainty() -> None:
    result = compare_prediction(
        10.2,
        Measurement(10.0, uncertainty=Uncertainty(0.3)),
        model="test-model",
    )
    assert result.verdict is PredictionVerdict.AGREEMENT
    assert result.absolute_error == 0.2
    assert result.normalized_error is not None


def test_prediction_discrepancy_exceeds_tolerance_and_uncertainty() -> None:
    result = compare_prediction(
        10.5,
        Measurement(10.0, uncertainty=Uncertainty(0.2), tolerance=0.1),
        model="test-model",
    )
    assert result.verdict is PredictionVerdict.DISCREPANCY
    assert result.absolute_error == 0.5
    assert result.normalized_error == 5 / 3


def test_zero_acceptance_bound_preserves_exact_comparison() -> None:
    result = compare_prediction(3.0, Measurement(3.0), model="test-model")
    assert result.verdict is PredictionVerdict.AGREEMENT
    assert result.normalized_error is None


def test_prediction_error_preserves_model_assumptions() -> None:
    result = compare_prediction(
        4.0,
        Measurement(4.2, tolerance=0.05),
        model="constant_acceleration_kinematics",
        assumptions=("acceleration remains constant",),
    )
    assert result.assumptions == ("acceleration remains constant",)
