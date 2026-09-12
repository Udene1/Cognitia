"""Newtonian force relationships as an explicit, testable model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .quantities import ACCELERATION, FORCE, MASS, Quantity


@dataclass(frozen=True)
class NewtonPrediction:
    """Predicted acceleration and the assumptions used to derive it."""

    acceleration: Quantity
    model: str
    assumptions: tuple[str, ...]


class NewtonianModel:
    """One-dimensional Newtonian dynamics: a = F_net / m."""

    name = "newtonian_second_law"
    assumptions: tuple[str, ...] = (
        "inertial reference frame",
        "classical Newtonian regime",
        "one-dimensional scalar forces",
    )

    def net_force(self, forces: Sequence[Quantity]) -> Quantity:
        if not forces:
            raise ValueError("at least one force is required")
        if any(force.dimension != FORCE for force in forces):
            raise ValueError("all forces must have FORCE dimension")
        total = Quantity(0.0, FORCE)
        for force in forces:
            total = total + force
        return total

    def predict(self, mass: Quantity, forces: Sequence[Quantity]) -> NewtonPrediction:
        if mass.dimension != MASS:
            raise ValueError("mass must have MASS dimension")
        if mass.value <= 0:
            raise ValueError("mass must be positive")
        net = self.net_force(forces)
        acceleration = net / mass
        if acceleration.dimension != ACCELERATION:
            raise ValueError("Newtonian derivation produced an invalid acceleration dimension")
        return NewtonPrediction(acceleration, self.name, self.assumptions)
