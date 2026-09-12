import pytest

from cognitia.physics import KinematicState, NewtonianDynamics, Quantity, FORCE, MASS


def test_force_is_derived_into_acceleration_then_kinematics():
    prediction = NewtonianDynamics().predict(
        KinematicState(velocity_mps=10.0),
        mass=Quantity(2.0, MASS),
        forces=(Quantity(10.0, FORCE),),
        duration_s=5.0,
    )

    assert prediction.state.acceleration_mps2 == pytest.approx(5.0)
    assert prediction.state.velocity_mps == pytest.approx(35.0)
    assert prediction.state.position_m == pytest.approx(112.5)
    assert prediction.derivation[1] == "divide net force by mass to derive acceleration"


def test_dynamics_preserves_model_chain_and_assumptions():
    prediction = NewtonianDynamics().predict(
        KinematicState(),
        mass=Quantity(2.0, MASS),
        forces=(Quantity(6.0, FORCE), Quantity(-2.0, FORCE)),
        duration_s=1.0,
    )

    assert prediction.state.acceleration_mps2 == pytest.approx(2.0)
    assert prediction.dynamics_model == "newtonian_second_law"
    assert prediction.kinematics_model == "constant_acceleration_kinematics"
    assert "inertial reference frame" in prediction.assumptions
    assert "acceleration remains constant" in prediction.assumptions
