"""Learning mechanisms built from Cognitia's accumulated experience."""

from .conditional import ConditionalPattern, ConditionalPatternLearner
from .hypothesis_search import HypothesisSearchLearner, SearchStrategy
from .model_revision import RevisionAction, RevisionDecision, revise_hypothesis
from .persistent_patterns import PersistentPatternLearner
from .persistent_solutions import PersistentSolutionPatternLearner
from .reasoning_patterns import ReasoningPattern, ReasoningPatternLearner
from .scientific import Hypothesis, ScientificEvaluator, TestResult
from .solution_patterns import SolutionPattern, SolutionPatternLearner
from .structural_transfer import StructuralPattern, StructuralTransferEngine, TransferCandidate, TransferVerification

__all__ = [
    "ConditionalPattern",
    "ConditionalPatternLearner",
    "HypothesisSearchLearner",
    "SearchStrategy",
    "PersistentPatternLearner",
    "PersistentSolutionPatternLearner",
    "ReasoningPattern",
    "ReasoningPatternLearner",
    "SolutionPattern",
    "SolutionPatternLearner",
    "Hypothesis",
    "ScientificEvaluator",
    "TestResult",
    "RevisionAction",
    "RevisionDecision",
    "revise_hypothesis",
    "StructuralPattern",
    "StructuralTransferEngine",
    "TransferCandidate",
    "TransferVerification",
]
