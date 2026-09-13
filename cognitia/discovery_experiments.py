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
    """Prefer tests where competing hypotheses make different predictions."""

    def select(self, predictions: tuple[Prediction, ...]) -> Experiment | None:
        if len(predictions) < 2:
            return None

        compatible: list[tuple[Prediction, Prediction]] = []
        for index, left in enumerate(predictions):
            for right in predictions[index + 1:]:
                if PredictionDeriver.is_discriminating(left, right):
                    compatible.append((left, right))
        if not compatible:
            return None

        best = max(compatible, key=self._information_gain)
        left, right = best
        return Experiment(
            id=f"experiment:{left.id}:{right.id}",
            condition=left.condition,
            objective="discriminate between competing predictions",
            predictions=(left, right),
            expected_information_gain=self._information_gain(best),
        )

    @staticmethod
    def _information_gain(pair: tuple[Prediction, Prediction]) -> float:
        """Normalize entropy reduction for two equally likely hypotheses.

        With two competing predictions and equal prior weight, disagreement gives
        one bit of expected information gain. Agreement would provide zero, but
        agreement is excluded by the discriminating-pair check.
        """
        left, right = pair
        if left.expected == right.expected:
            return 0.0
        prior_entropy = 1.0  # H([0.5, 0.5]) = 1 bit.
        outcome_entropy = 0.0  # deterministic prediction partitions under the pair.
        return min(1.0, max(0.0, (prior_entropy - outcome_entropy) / prior_entropy))
