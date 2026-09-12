"""Cognitia: experimental artificial cognitive system."""

from .acquisition import AcquisitionProposal, AcquisitionStage, CapabilityRequirement, propose_capability_acquisition
from .acquisition_engine import AcquisitionDecision, AcquisitionPlan, CapabilityAcquisitionEngine, CapabilityGapSignal
from .benchmark import BenchmarkCase, BenchmarkOutcome, BenchmarkResult, BenchmarkSuite, BuildComparison, CaseResult, compare_builds
from .build import CapabilityRecord, CognitiveBuild, create_build
from .candidate_pipeline import CandidateEvaluation, benchmark_candidate, evaluate_candidate
from .candidate_registry import CandidateRecord, CandidateRegistry, CandidateState
from .capability_acquisition import AcquisitionMode, CapabilityCandidate, Operation, ReasoningTrace, compose_capability, construct_capability, learn_procedure
from .learning.transfer import TransferAssessment, assess_transfer
from .regression import PromotionDecision, RegressionFinding, RegressionPolicy, evaluate_promotion
from .verification import VerificationOutcome, VerificationPlan, VerificationResult, VerificationStep, execute_plan

__version__ = "0.1.0"

__all__ = [
    "AcquisitionProposal", "AcquisitionStage", "CapabilityRequirement", "propose_capability_acquisition",
    "AcquisitionDecision", "AcquisitionPlan", "CapabilityAcquisitionEngine", "CapabilityGapSignal",
    "AcquisitionMode", "CapabilityCandidate", "Operation", "ReasoningTrace", "compose_capability", "construct_capability", "learn_procedure",
    "CandidateEvaluation", "benchmark_candidate", "evaluate_candidate", "CandidateRecord", "CandidateRegistry", "CandidateState",
    "BenchmarkCase", "BenchmarkOutcome", "BenchmarkResult", "BenchmarkSuite", "BuildComparison", "CaseResult", "compare_builds",
    "CapabilityRecord", "CognitiveBuild", "create_build",
    "TransferAssessment", "assess_transfer",
    "VerificationOutcome", "VerificationPlan", "VerificationResult", "VerificationStep", "execute_plan",
    "PromotionDecision", "RegressionFinding", "RegressionPolicy", "evaluate_promotion", "__version__",
]
