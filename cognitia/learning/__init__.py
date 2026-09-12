"""Learning mechanisms built from Cognitia's accumulated experience."""

from .conditional import ConditionalPattern, ConditionalPatternLearner
from .model_revision import RevisionAction, RevisionDecision, revise_hypothesis
from .persistent_patterns import PersistentPatternLearner
from .scientific import Hypothesis, ScientificEvaluator, TestResult

__all__ = [
    "ConditionalPattern",
    "ConditionalPatternLearner",
    "PersistentPatternLearner",
    "Hypothesis",
    "ScientificEvaluator",
    "TestResult",
    "RevisionAction",
    "RevisionDecision",
    "revise_hypothesis",
]
