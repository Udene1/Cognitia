"""Physical quantities with explicit SI dimensions.

Cognitia must not treat physical numbers as dimensionless values. A quantity
carries its dimensions so invalid operations fail before they become a false
physical prediction.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Dimension:
    """SI base-dimension exponents in the order M, L, T."""

    mass: int = 0
    length: int = 0
    time: int = 0

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(
            self.mass + other.mass,
            self.length + other.length,
            self.time + other.time,
        )

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(
            self.mass - other.mass,
            self.length - other.length,
            self.time - other.time,
        )

    def __pow__(self, exponent: int) -> "Dimension":
        return Dimension(
            self.mass * exponent,
            self.length * exponent,
            self.time * exponent,
        )


DIMENSIONLESS = Dimension()
MASS = Dimension(mass=1)
LENGTH = Dimension(length=1)
TIME = Dimension(time=1)
VELOCITY = LENGTH / TIME
ACCELERATION = LENGTH / (TIME**2)
FORCE = MASS * ACCELERATION


@dataclass(frozen=True)
class Quantity:
    """A finite numerical value paired with an SI dimension."""

    value: float
    dimension: Dimension

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise ValueError("quantity value must be finite")

    def __add__(self, other: "Quantity") -> "Quantity":
        if self.dimension != other.dimension:
            raise ValueError("cannot add quantities with different dimensions")
        return Quantity(self.value + other.value, self.dimension)

    def __sub__(self, other: "Quantity") -> "Quantity":
        if self.dimension != other.dimension:
            raise ValueError("cannot subtract quantities with different dimensions")
        return Quantity(self.value - other.value, self.dimension)

    def __mul__(self, other: "Quantity") -> "Quantity":
        return Quantity(self.value * other.value, self.dimension * other.dimension)

    def __truediv__(self, other: "Quantity") -> "Quantity":
        if other.value == 0:
            raise ZeroDivisionError("cannot divide by a zero quantity")
        return Quantity(self.value / other.value, self.dimension / other.dimension)
