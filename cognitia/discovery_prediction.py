"""Falsifiable prediction primitives for discovery candidates."""
from __future__ import annotations

from dataclasses import dataclass

from .discovery import HypothesisCandidate


@dataclass(frozen=True)
class Prediction:
    """A predicted observation with an explicit condition and outcome."""

    id: str
    hypothesis_id: str
    condition: str
    expected: str
    falsifier: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.id, self.hypothesis_id, self.condition, self.expected, self.falsifier)):
            raise ValueError("prediction fields are required")


class PredictionDeriver:
    """Turn a structured hypothesis into a testable prediction contract.

    The derivation is intentionally conservative: callers provide the condition,
    expected outcome and falsifier. Cognitia records the prediction rather than
    pretending that a natural-language proposition automatically implies a
    scientific prediction.
    """

    def derive(
        self,
        hypothesis: HypothesisCandidate,
        *,
        condition: str,
        expected: str,
        falsifier: str,
    ) -> Prediction:
        prediction_id = f"{hypothesis.id}:p{len(hypothesis.predictions) + 1}"
        return Prediction(
            id=prediction_id,
            hypothesis_id=hypothesis.id,
            condition=condition,
            expected=expected,
            falsifier=falsifier,
        )

    @staticmethod
    def is_discriminating(left: Prediction, right: Prediction) -> bool:
        """Return true only when the predictions disagree under the same condition."""
        return left.condition == right.condition and left.expected != right.expected
