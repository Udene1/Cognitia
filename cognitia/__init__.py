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
from .durable import DurableEvent, SQLiteCognitiveJournal
from .durable_cognition import DurableCognitiveLedger
from .discovery import DiscoveryWorkspace, ExplanationAssessment, ExplanationStatus, ExplanatoryGap, HypothesisCandidate, Observation, unresolved_observations
from .discovery_artifact import DiscoveryArtifact, DurableDiscoveryArtifacts
from .discovery_experiments import DiscriminatingExperimentSelector, Experiment
from .discovery_hypotheses import ExplanatoryModel, HypothesisAlternative, HypothesisSpaceBuilder, HypothesisTransform
from .discovery_prediction import Prediction, PredictionDeriver
from .discovery_search import DiscoverySearchEngine, SearchBudget, SearchCandidate, normalized_entropy
from .discovery_structure import ModelElement, ModelRelation, RelationKind, StructuralAlternative, StructuralHypothesisBuilder, StructuralModel
from .discovery_ir import DiscoveryIR, DiscoveryIRBuilder, IRNode, IRRelation
from .discovery_investigation import DiscoveryInvestigator, InvestigationResult
from .discovery_failures import DiscoveryFailure, DiscoveryFailureLearner
from .discovery_knowledge import DiscoveryKnowledgePromoter, KnowledgePromotionDecision
from .environment import EnvironmentObservation, EnvironmentSource, NullEnvironmentSource
from .parallel_investigation import InvestigationTask, InvestigationResult as ParallelInvestigationResult, ParallelInvestigator
from .web_evidence import EvidenceAssessment, WebEvidenceEvaluator
from .web_search import SearchQuery, WebEnvironmentSource, WebSearchProvider
from .evidence import Claim, EvidenceRecord, EvidenceSource, SourceLineage, EvidenceGraph, EvidenceRelation, EvidenceConvergenceEngine, ConvergenceAssessment, ModelConstraint, ModelConsistencyChecker, ModelCheckResult
from .failure_analysis import CapabilityGapDiagnosis, FailureAnalyzer, FailureClass, FailureObservation
from .git_environment import GitCommitObservation, GitEnvironmentError, GitHistoryIngestor, GitRepositoryObserver
from .learning import HypothesisSearchLearner, PersistentPatternLearner, SearchStrategy
from .git_knowledge import GitKnowledgeIngestor
from .learning.transfer import TransferAssessment, assess_transfer
from .knowledge.model import KnowledgeItem, KnowledgeSource
from .knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore
from .language import AnswerContract, EntityMention, EventMention, LanguageFrame, QuestionAnalysis, RelationMention, SemanticProposition, TextToken, analyze_question, build_language_frame
from .answer_contract import AnswerAssessment, AnswerContractPlanner, AnswerPlan, plan_answer
from .promotion import CognitivePromotionOrchestrator, PromotionEvaluation
from .replay import CognitiveStateReplayer, RecoveredCognitiveState
from .regression import CandidateDisposition, PromotionDecision, RegressionFinding, RegressionPolicy, evaluate_promotion
from .verification import VerificationOutcome, VerificationPlan, VerificationResult, VerificationStep, execute_plan
from .logic_ir import LogicModel, LogicNode, LogicRelation, LogicProvenance, LogicTransferCandidate, LogicTransferEngine, LogicTransferVerification, TransferMapping, model_from_parts
from .logic_adapters import CodeLogicAdapter, LogicAdapterResult, MathLogicAdapter, TextLogicAdapter, UniversalLogicAdapter
from .learning.concept_transfer import GenericLogicExtractor

__version__ = "0.1.0"

__all__ = [
    "AcquisitionProposal", "AcquisitionStage", "CapabilityRequirement", "propose_capability_acquisition", "AcquisitionDecision", "AcquisitionPlan", "CapabilityAcquisitionEngine", "CapabilityGapSignal",
    "BalancingEngine", "BalancingProposal", "BalancingStrategy", "RepairPolicy", "AcquisitionMode", "CapabilityCandidate", "Operation", "ReasoningTrace", "compose_capability", "construct_capability", "learn_procedure", "CandidateEvaluation", "benchmark_candidate", "evaluate_candidate", "CandidateRecord", "CandidateRegistry", "CandidateState",
    "BenchmarkCase", "BenchmarkOutcome", "BenchmarkResult", "BenchmarkSuite", "BuildComparison", "CaseResult", "compare_builds", "CapabilityRecord", "CognitiveBuild", "create_build", "CognitiveHistory", "EvaluationRecord", "PromotionEvent", "evaluation_from_comparison",
    "EngineeringEvent", "EngineeringExperienceRecorder", "engineering_memory", "DurableEvent", "SQLiteCognitiveJournal", "DurableCognitiveLedger", "DiscoveryWorkspace", "ExplanationAssessment", "ExplanationStatus", "ExplanatoryGap", "HypothesisCandidate", "Observation", "unresolved_observations",
    "DiscoveryArtifact", "DurableDiscoveryArtifacts", "DiscoveryIR", "DiscoveryIRBuilder", "IRNode", "IRRelation", "ExplanatoryModel", "HypothesisAlternative", "HypothesisSpaceBuilder", "HypothesisTransform", "Prediction", "PredictionDeriver", "DiscriminatingExperimentSelector", "Experiment", "DiscoverySearchEngine", "SearchBudget", "SearchCandidate", "normalized_entropy",
    "ModelElement", "ModelRelation", "RelationKind", "StructuralAlternative", "StructuralHypothesisBuilder", "StructuralModel", "DiscoveryInvestigator", "InvestigationResult", "DiscoveryFailure", "DiscoveryFailureLearner", "DiscoveryKnowledgePromoter", "KnowledgePromotionDecision",
    "EnvironmentObservation", "EnvironmentSource", "NullEnvironmentSource", "InvestigationTask", "ParallelInvestigationResult", "ParallelInvestigator", "SearchQuery", "WebEnvironmentSource", "WebSearchProvider", "EvidenceAssessment", "WebEvidenceEvaluator",
    "Claim", "EvidenceRecord", "EvidenceSource", "SourceLineage", "EvidenceGraph", "EvidenceRelation", "EvidenceConvergenceEngine", "ConvergenceAssessment", "ModelConstraint", "ModelConsistencyChecker", "ModelCheckResult",
    "CognitiveStateReplayer", "RecoveredCognitiveState", "GitCommitObservation", "GitEnvironmentError", "GitHistoryIngestor", "GitRepositoryObserver", "GitKnowledgeIngestor", "PersistentPatternLearner", "HypothesisSearchLearner", "SearchStrategy", "KnowledgeItem", "KnowledgeSource", "KnowledgeTest", "ValidatedKnowledgeStore",
    "TextToken", "EntityMention", "EventMention", "RelationMention", "LanguageFrame", "SemanticProposition", "QuestionAnalysis", "AnswerContract", "build_language_frame", "analyze_question", "AnswerAssessment", "AnswerContractPlanner", "AnswerPlan", "plan_answer",
    "FailureClass", "FailureObservation", "FailureAnalyzer", "CapabilityGapDiagnosis", "TransferAssessment", "assess_transfer", "VerificationOutcome", "VerificationPlan", "VerificationResult", "VerificationStep", "execute_plan", "CandidateDisposition", "PromotionDecision", "RegressionFinding", "RegressionPolicy", "evaluate_promotion", "CognitivePromotionOrchestrator", "PromotionEvaluation",
    "LogicModel", "LogicNode", "LogicRelation", "LogicProvenance", "LogicTransferCandidate", "LogicTransferEngine", "LogicTransferVerification", "TransferMapping", "model_from_parts", "LogicAdapterResult", "TextLogicAdapter", "CodeLogicAdapter", "MathLogicAdapter", "UniversalLogicAdapter", "GenericLogicExtractor", "__version__",
]
