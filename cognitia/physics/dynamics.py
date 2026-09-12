"""Bridge forces to kinematics without hiding the derivation trace."""
from __future__ import annotations

from dataclasses import dataclass

from .mechanics import KinematicState, KinematicsModel
from .newton import NewtonianModel
from .quantities import Quantity


@dataclass(frozen=True)
class DynamicsPrediction:
    """A kinematic prediction together with its force-to-acceleration derivation."""

    state: KinematicState
    dynamics_model: str
    kinematics_model: str
    derivation: tuple[str, ...]
    assumptions: tuple[str, ...]


class NewtonianDynamics:
    """Compose Newtonian dynamics with constant-acceleration kinematics."""

    def __init__(self) -> None:
        self._dynamics = NewtonianModel()
        self._kinematics = KinematicsModel()

    def predict(
        self,
        state: KinematicState,
        *,
        mass: Quantity,
        forces: tuple[Quantity, ...],
        duration_s: float,
    ) -> DynamicsPrediction:
        dynamics = self._dynamics.predict(mass, forces)
        kinematic_state = KinematicState(
            position_m=state.position_m,
            velocity_mps=state.velocity_mps,
            acceleration_mps2=dynamics.acceleration.value,
            time_s=state.time_s,
        )
        prediction = self._kinematics.predict(kinematic_state, duration_s=duration_s)
        return DynamicsPrediction(
            state=prediction.state,
            dynamics_model=dynamics.model,
            kinematics_model=prediction.model,
            derivation=(
                "sum applied forces to obtain net force",
                "divide net force by mass to derive acceleration",
                "use derived acceleration in constant-acceleration kinematics",
            ),
            assumptions=tuple(dict.fromkeys(dynamics.assumptions + prediction.assumptions)),
        )
