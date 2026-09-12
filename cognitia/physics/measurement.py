"""Measurements, uncertainty, and prediction error for physical models.

Exact equality is not a defensible default for empirical physics. This module
keeps the observed value, uncertainty, tolerance, and comparison outcome
explicit so model evaluation can distinguish agreement from meaningful error.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math


@dataclass(frozen=True)
class Uncertainty:
    """Non-negative absolute uncertainty in the same units as a measurement."""

    absolute: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.absolute) or self.absolute < 0:
            raise ValueError("absolute uncertainty must be finite and non-negative")


@dataclass(frozen=True)
class Measurement:
    """An observed quantity with explicit uncertainty and optional tolerance."""

    value: float
    uncertainty: Uncertainty = Uncertainty(0.0)
    tolerance: float = 0.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise ValueError("measurement value must be finite")
        if not math.isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("tolerance must be finite and non-negative")

    @property
    def acceptance_bound(self) -> float:
        return self.uncertainty.absolute + self.tolerance


class PredictionVerdict(str, Enum):
    AGREEMENT = "agreement"
    DISCREPANCY = "discrepancy"


@dataclass(frozen=True)
class PredictionError:
    """Comparison of a model prediction against an observation."""

    predicted: float
    observed: Measurement
    absolute_error: float
    normalized_error: float | None
    verdict: PredictionVerdict
    model: str
    assumptions: tuple[str, ...] = ()


def compare_prediction(
    predicted: float,
    observed: Measurement,
    *,
    model: str,
    assumptions: tuple[str, ...] = (),
) -> PredictionError:
    """Compare a prediction using measurement uncertainty plus tolerance.

    A prediction agrees when its absolute error does not exceed the explicit
    acceptance bound. A zero bound therefore requires exact equality, while
    real measurements can specify a physically meaningful tolerance.

    Error values are kept at full floating-point precision so callers can
    reason from the actual ratio rather than a presentation-rounded value.
    """
    if not math.isfinite(predicted):
        raise ValueError("predicted value must be finite")
    if not model.strip():
        raise ValueError("model is required")

    error = abs(predicted - observed.value)
    bound = observed.acceptance_bound
    verdict = PredictionVerdict.AGREEMENT if error <= bound else PredictionVerdict.DISCREPANCY
    normalized = None if bound == 0 else error / bound
    return PredictionError(
        predicted=predicted,
        observed=observed,
        absolute_error=error,
        normalized_error=normalized,
        verdict=verdict,
        model=model,
        assumptions=assumptions,
    )
