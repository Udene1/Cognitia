"""Cognitia: experimental artificial cognitive system."""

from .acquisition import AcquisitionProposal, AcquisitionStage, CapabilityRequirement, propose_capability_acquisition
from .acquisition_engine import AcquisitionDecision, AcquisitionPlan, CapabilityAcquisitionEngine, CapabilityGapSignal
from .balancing import BalancingEngine, BalancingProposal, BalancingStrategy, RepairPolicy
from .benchmark import BenchmarkCase, BenchmarkOutcome, BenchmarkResult, BenchmarkSuite, BuildComparison, CaseResult, compare_builds
from .build import CapabilityRecord, CognitiveBuild, create_build
from .candidate_pipeline import CandidateEvaluation, benchmark_candidate, evaluate_candidate
from .candidate_registry import CandidateRecord, CandidateRegistry, CandidateState
from .capability_acquisition import AcquisitionMode, CapabilityCandidate, Operation, ReasoningTrace, compose_capability, construct_capability, learn_procedure
from .cognitive_history import CognitiveHistory, EvaluationRecord, PromotionEvent, evaluation_from_comparison
from .engineering import EngineeringEvent, EngineeringExperienceRecorder, engineering_memory
from .failure_analysis import CapabilityGapDiagnosis, FailureAnalyzer, FailureClass, FailureObservation
from .learning.transfer import TransferAssessment, assess_transfer
from .promotion import CognitivePromotionOrchestrator, PromotionEvaluation
from .regression import CandidateDisposition, PromotionDecision, RegressionFinding, RegressionPolicy, evaluate_promotion
from .verification import VerificationOutcome, VerificationPlan, VerificationResult, VerificationStep, execute_plan

__version__ = "0.1.0"

__all__ = [
    "AcquisitionProposal", "AcquisitionStage", "CapabilityRequirement", "propose_capability_acquisition",
    "AcquisitionDecision", "AcquisitionPlan", "CapabilityAcquisitionEngine", "CapabilityGapSignal",
    "BalancingEngine", "BalancingProposal", "BalancingStrategy", "RepairPolicy",
    "AcquisitionMode", "CapabilityCandidate", "Operation", "ReasoningTrace", "compose_capability", "construct_capability", "learn_procedure",
    "CandidateEvaluation", "benchmark_candidate", "evaluate_candidate", "CandidateRecord", "CandidateRegistry", "CandidateState",
    "BenchmarkCase", "BenchmarkOutcome", "BenchmarkResult", "BenchmarkSuite", "BuildComparison", "CaseResult", "compare_builds",
    "CapabilityRecord", "CognitiveBuild", "create_build",
    "CognitiveHistory", "EvaluationRecord", "PromotionEvent", "evaluation_from_comparison",
    "EngineeringEvent", "EngineeringExperienceRecorder", "engineering_memory",
    "FailureClass", "FailureObservation", "FailureAnalyzer", "CapabilityGapDiagnosis",
    "TransferAssessment", "assess_transfer",
    "VerificationOutcome", "VerificationPlan", "VerificationResult", "VerificationStep", "execute_plan",
    "CandidateDisposition", "PromotionDecision", "RegressionFinding", "RegressionPolicy", "evaluate_promotion",
    "CognitivePromotionOrchestrator", "PromotionEvaluation", "__version__",
]
