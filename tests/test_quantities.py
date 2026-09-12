import pytest

from cognitia.physics import ACCELERATION, FORCE, LENGTH, MASS, TIME, VELOCITY, Quantity


def test_dimension_algebra_builds_expected_physical_dimensions():
    assert (LENGTH / TIME) == VELOCITY
    assert (LENGTH / (TIME**2)) == ACCELERATION
    assert (MASS * ACCELERATION) == FORCE


def test_addition_requires_matching_dimensions():
    distance = Quantity(10.0, LENGTH)
    more_distance = Quantity(2.0, LENGTH)

    assert (distance + more_distance).value == 12.0

    with pytest.raises(ValueError, match="different dimensions"):
        _ = distance + Quantity(2.0, TIME)


def test_multiplication_and_division_compose_dimensions():
    force = Quantity(10.0, FORCE)
    mass = Quantity(2.0, MASS)

    acceleration = force / mass

    assert acceleration.value == 5.0
    assert acceleration.dimension == ACCELERATION
