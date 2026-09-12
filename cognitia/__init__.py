"""Cognitia: experimental artificial cognitive system."""

from .acquisition import (
    AcquisitionProposal,
    AcquisitionStage,
    CapabilityRequirement,
    propose_capability_acquisition,
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

__version__ = "0.1.0"

__all__ = [
    "AcquisitionProposal",
    "AcquisitionStage",
    "CapabilityRequirement",
    "propose_capability_acquisition",
    "BenchmarkCase",
    "BenchmarkOutcome",
    "BenchmarkResult",
    "BenchmarkSuite",
    "BuildComparison",
    "CaseResult",
    "compare_builds",
    "__version__",
]
