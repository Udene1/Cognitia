"""Deterministic one-dimensional Newtonian kinematics.

This is intentionally a model, not a physics encyclopedia. It turns an
explicit physical state and assumptions into a prediction that Cognitia can
later test against observations.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KinematicState:
    """One-dimensional physical state using SI units.

    position: metres
    velocity: metres/second
    acceleration: metres/second squared
    time: seconds
    """

    position_m: float = 0.0
    velocity_mps: float = 0.0
    acceleration_mps2: float = 0.0
    time_s: float = 0.0

    def __post_init__(self) -> None:
        if self.time_s < 0:
            raise ValueError("time_s cannot be negative")


@dataclass(frozen=True)
class Prediction:
    """A predicted state plus the assumptions that produced it."""

    state: KinematicState
    model: str
    assumptions: tuple[str, ...]


class KinematicsModel:
    """Predict constant-acceleration motion from an explicit initial state."""

    name = "constant_acceleration_kinematics"

    def predict(self, state: KinematicState, *, duration_s: float) -> Prediction:
        """Predict position and velocity after ``duration_s`` seconds.

        Uses v = u + at and s = ut + 1/2 at². The model is only valid under
        its explicit constant-acceleration assumption; it does not silently
        infer forces or invent missing physical conditions.
        """
        if duration_s < 0:
            raise ValueError("duration_s cannot be negative")

        acceleration = state.acceleration_mps2
        velocity = state.velocity_mps + acceleration * duration_s
        position = (
            state.position_m
            + state.velocity_mps * duration_s
            + 0.5 * acceleration * duration_s**2
        )
        next_state = KinematicState(
            position_m=position,
            velocity_mps=velocity,
            acceleration_mps2=acceleration,
            time_s=state.time_s + duration_s,
        )
        return Prediction(
            state=next_state,
            model=self.name,
            assumptions=("acceleration remains constant", "motion is one-dimensional"),
        )
