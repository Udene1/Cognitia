from cognitia.physics import (
    KinematicState,
    Measurement,
    NewtonianDynamics,
    Quantity,
    Uncertainty,
    compare_prediction,
)
from cognitia.physics.quantities import FORCE, MASS


def test_dynamics_prediction_can_be_tested_against_an_observation() -> None:
    prediction = NewtonianDynamics().predict(
        KinematicState(position_m=0.0, velocity_mps=2.0),
        mass=Quantity(2.0, MASS),
        forces=(Quantity(10.0, FORCE),),
        duration_s=3.0,
    )

    assessment = compare_prediction(
        prediction.state.velocity_mps,
        Measurement(16.2, uncertainty=Uncertainty(0.25)),
        model=prediction.dynamics_model,
        assumptions=prediction.assumptions,
    )

    assert assessment.verdict.value == "agreement"
    assert assessment.absolute_error == 0.2
    assert "acceleration remains constant" in assessment.assumptions


def test_prediction_error_can_expose_a_model_discrepancy() -> None:
    prediction = NewtonianDynamics().predict(
        KinematicState(position_m=0.0, velocity_mps=0.0),
        mass=Quantity(2.0, MASS),
        forces=(Quantity(10.0, FORCE),),
        duration_s=2.0,
    )

    assessment = compare_prediction(
        prediction.state.position_m,
        Measurement(12.0, uncertainty=Uncertainty(0.1)),
        model=prediction.kinematics_model,
        assumptions=prediction.assumptions,
    )

    assert assessment.verdict.value == "discrepancy"
    assert assessment.absolute_error == 2.0
