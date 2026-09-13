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
    """Prefer tests whose outcomes reduce uncertainty between hypotheses."""

    def select(
        self,
        predictions: tuple[Prediction, ...],
        *,
        priors: tuple[float, ...] | None = None,
    ) -> Experiment | None:
        if len(predictions) < 2:
            return None
        if priors is not None and len(priors) != len(predictions):
            raise ValueError("priors must match prediction count")
        compatible = []
        for index, left in enumerate(predictions):
            for right in predictions[index + 1:]:
                if PredictionDeriver.is_discriminating(left, right):
                    gain = self._information_gain(
                        (left, right),
                        self._pair_priors(priors, index, index + 1),
                    )
                    compatible.append((gain, left, right))
        if not compatible:
            return None
        gain, left, right = max(compatible, key=lambda item: (item[0], item[1].id, item[2].id))
        return Experiment(
            id=f"experiment:{left.id}:{right.id}",
            condition=left.condition,
            objective="discriminate between competing predictions",
            predictions=(left, right),
            expected_information_gain=gain,
        )

    @staticmethod
    def _pair_priors(priors: tuple[float, ...] | None, left: int, right: int) -> tuple[float, float]:
        if priors is None:
            return (0.5, 0.5)
        a, b = priors[left], priors[right]
        total = a + b
        if a < 0 or b < 0 or total <= 0:
            raise ValueError("selected hypothesis priors must be non-negative and non-zero")
        return (a / total, b / total)

    @staticmethod
    def _information_gain(pair: tuple[Prediction, Prediction], priors: tuple[float, float]) -> float:
        """Expected entropy reduction when competing deterministic outcomes disagree."""
        left, right = pair
        if left.expected == right.expected:
            return 0.0
        prior_entropy = -sum(p * log2(p) for p in priors if p > 0)
        if prior_entropy == 0.0:
            return 0.0
        # A discriminating deterministic outcome identifies the member of the pair.
        return min(1.0, max(0.0, prior_entropy / prior_entropy))
