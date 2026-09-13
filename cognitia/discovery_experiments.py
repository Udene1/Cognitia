"""Selection of experiments that discriminate between hypotheses."""
from __future__ import annotations

from dataclasses import dataclass
from math import log2

from .discovery_prediction import Prediction, PredictionDeriver


@dataclass(frozen=True)
class Experiment:
    id: str
    condition: str
    objective: str
    predictions: tuple[Prediction, ...]
    expected_information_gain: float

    def __post_init__(self) -> None:
        if not self.id or not self.condition.strip() or not self.objective.strip():
            raise ValueError("experiment identity, condition and objective are required")
        if len(self.predictions) < 2:
            raise ValueError("a discriminating experiment needs at least two predictions")
        if not 0.0 <= self.expected_information_gain <= 1.0:
            raise ValueError("expected information gain must be between 0 and 1")


class DiscriminatingExperimentSelector:
    """Prefer tests whose deterministic outcomes reduce hypothesis uncertainty."""

    def select(self, predictions: tuple[Prediction, ...], *, priors: tuple[float, ...] | None = None) -> Experiment | None:
        if len(predictions) < 2:
            return None
        if priors is not None:
            if len(priors) != len(predictions):
                raise ValueError("priors must match prediction count")
            if any(p < 0 for p in priors) or sum(priors) <= 0:
                raise ValueError("priors must be non-negative and non-zero")
        compatible: list[tuple[float, Prediction, Prediction]] = []
        for left_index, left in enumerate(predictions):
            for right_index in range(left_index + 1, len(predictions)):
                right = predictions[right_index]
                if PredictionDeriver.is_discriminating(left, right):
                    gain = self._information_gain((left, right), self._pair_priors(priors, left_index, right_index))
                    compatible.append((gain, left, right))
        if not compatible:
            return None
        gain, left, right = max(compatible, key=lambda item: (item[0], item[1].id, item[2].id))
        return Experiment(
            id=f"experiment:{left.id}:{right.id}", condition=left.condition,
            objective="discriminate between competing predictions", predictions=(left, right),
            expected_information_gain=gain,
        )

    @staticmethod
    def _pair_priors(priors: tuple[float, ...] | None, left: int, right: int) -> tuple[float, float]:
        if priors is None:
            return (0.5, 0.5)
        a, b = priors[left], priors[right]
        total = a + b
        if total <= 0:
            raise ValueError("selected hypothesis priors must sum to a positive value")
        return (a / total, b / total)

    @staticmethod
    def _information_gain(pair: tuple[Prediction, Prediction], priors: tuple[float, float]) -> float:
        if pair[0].expected == pair[1].expected:
            return 0.0
        # For two mutually exclusive deterministic predictions, the outcome
        # identifies the surviving hypothesis. One bit is the normalization unit.
        entropy = -sum(p * log2(p) for p in priors if p > 0)
        return min(1.0, max(0.0, entropy))
