"""Selection of experiments that discriminate between hypotheses."""
from __future__ import annotations

from dataclasses import dataclass

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

        left, right = compatible[0]
        return Experiment(
            id=f"experiment:{left.id}:{right.id}",
            condition=left.condition,
            objective="discriminate between competing predictions",
            predictions=(left, right),
            expected_information_gain=0.5,
        )
