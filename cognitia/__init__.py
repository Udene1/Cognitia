"""Cognitia: experimental artificial cognitive system."""

from .acquisition import (
    AcquisitionProposal,
    AcquisitionStage,
    CapabilityRequirement,
    propose_capability_acquisition,
)
from .acquisition_engine import (
    AcquisitionDecision,
    AcquisitionPlan,
    CapabilityAcquisitionEngine,
    CapabilityGapSignal,
)
from .benchmark import (
    BenchmarkCase,
    BenchmarkOutcome,
    BenchmarkResult,
    BenchmarkSuite,
    BuildComparison,
    CaseResult,
    compare_builds,
)
from .build import CapabilityRecord, CognitiveBuild, create_build
from .capability_acquisition import (
    AcquisitionMode,
    CapabilityCandidate,
    Operation,
    ReasoningTrace,
    compose_capability,
    construct_capability,
    learn_procedure,
)
from .regression import (
    PromotionDecision,
    RegressionFinding,
    RegressionPolicy,
    evaluate_promotion,
)

__version__ = "0.1.0"

__all__ = [
    "AcquisitionProposal",
    "AcquisitionStage",
    "CapabilityRequirement",
    "propose_capability_acquisition",
    "AcquisitionDecision",
    "AcquisitionPlan",
    "CapabilityAcquisitionEngine",
    "CapabilityGapSignal",
    "AcquisitionMode",
    "CapabilityCandidate",
    "Operation",
    "ReasoningTrace",
    "compose_capability",
    "construct_capability",
    "learn_procedure",
    "BenchmarkCase",
    "BenchmarkOutcome",
    "BenchmarkResult",
    "BenchmarkSuite",
    "BuildComparison",
    "CaseResult",
    "compare_builds",
    "CapabilityRecord",
    "CognitiveBuild",
    "create_build",
    "PromotionDecision",
    "RegressionFinding",
    "RegressionPolicy",
    "evaluate_promotion",
    "__version__",
]
