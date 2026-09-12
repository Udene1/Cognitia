"""Turn prediction discrepancies into structured model evidence.

This layer deliberately does not change beliefs. It records what a prediction
said, what was observed, how large the discrepancy was, and what epistemic
consequence the observation can justify.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .measurement import PredictionError, PredictionVerdict


class ModelEvidence(str, Enum):
    SUPPORTING = "supporting"
    CHALLENGING = "challenging"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class ModelEvaluation:
    """Evidence about a model produced by one explicit prediction test."""

    model: str
    evidence: ModelEvidence
    prediction_error: PredictionError
    reason: str
    condition: str = ""


def evaluate_prediction(
    prediction_error: PredictionError,
    *,
    condition: str = "",
) -> ModelEvaluation:
    """Classify empirical evidence without silently revising model confidence.

    Agreement is supporting evidence. A discrepancy is challenging evidence,
    but it does not by itself establish that the model is false: measurement
    quality, assumptions, omitted variables, and domain validity still matter.
    """
    if prediction_error.verdict is PredictionVerdict.AGREEMENT:
        evidence = ModelEvidence.SUPPORTING
        reason = "Prediction falls within the declared measurement uncertainty and tolerance."
    else:
        evidence = ModelEvidence.CHALLENGING
        reason = (
            "Prediction lies outside the declared acceptance bound; investigate "
            "measurement quality, assumptions, omitted variables, and model domain."
        )
    return ModelEvaluation(
        model=prediction_error.model,
        evidence=evidence,
        prediction_error=prediction_error,
        reason=reason,
        condition=condition,
    )
