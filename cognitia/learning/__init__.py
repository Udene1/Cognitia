"""Learning mechanisms built from Cognitia's accumulated experience."""

from .conditional import ConditionalPattern, ConditionalPatternLearner
from .scientific import Hypothesis, ScientificEvaluator, TestResult

__all__ = [
    "ConditionalPattern",
    "ConditionalPatternLearner",
    "Hypothesis",
    "ScientificEvaluator",
    "TestResult",
]
