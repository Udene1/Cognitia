import pytest

from cognitia.physics import KinematicState, KinematicsModel


def test_constant_acceleration_predicts_velocity_and_position():
    prediction = KinematicsModel().predict(
        KinematicState(velocity_mps=10.0, acceleration_mps2=2.0),
        duration_s=5.0,
    )

    assert prediction.state.velocity_mps == pytest.approx(20.0)
    assert prediction.state.position_m == pytest.approx(75.0)
    assert prediction.state.time_s == pytest.approx(5.0)


def test_prediction_preserves_explicit_model_assumptions():
    prediction = KinematicsModel().predict(
        KinematicState(position_m=3.0),
        duration_s=2.0,
    )

    assert prediction.model == "constant_acceleration_kinematics"
    assert "acceleration remains constant" in prediction.assumptions
    assert "motion is one-dimensional" in prediction.assumptions


def test_negative_duration_is_rejected():
    with pytest.raises(ValueError, match="duration_s cannot be negative"):
        KinematicsModel().predict(KinematicState(), duration_s=-1.0)
