import pytest

from cognitia.physics import FORCE, LENGTH, MASS, NewtonianModel, Quantity


def test_newton_second_law_derives_acceleration():
    prediction = NewtonianModel().predict(Quantity(2.0, MASS), (Quantity(10.0, FORCE),))

    assert prediction.acceleration.value == 5.0
    assert prediction.acceleration.dimension == FORCE / MASS
    assert prediction.model == "newtonian_second_law"


def test_net_force_composes_opposing_forces():
    prediction = NewtonianModel().predict(
        Quantity(2.0, MASS),
        (Quantity(10.0, FORCE), Quantity(-4.0, FORCE)),
    )

    assert prediction.acceleration.value == 3.0


def test_newton_rejects_invalid_mass_and_force_dimensions():
    model = NewtonianModel()
    with pytest.raises(ValueError):
        model.predict(Quantity(0.0, MASS), (Quantity(10.0, FORCE),))
    with pytest.raises(ValueError):
        model.predict(Quantity(2.0, LENGTH), (Quantity(10.0, FORCE),))
    with pytest.raises(ValueError):
        model.predict(Quantity(2.0, MASS), (Quantity(10.0, LENGTH),))
