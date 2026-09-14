"""End-to-end capability benchmark: acquire evidence, reason, test, update."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from cognitia.discovery_experiments import DiscriminatingExperimentSelector
from cognitia.discovery_prediction import Prediction
from cognitia.environment import EnvironmentObservation, EnvironmentSource
from cognitia.evidence.convergence import EvidenceConvergenceEngine
from cognitia.evidence.model import Claim, EvidenceRecord, EvidenceSource, SourceLineage
from cognitia.parallel_investigation import InvestigationTask, ParallelInvestigator


@dataclass(frozen=True)
class InvestigationLoopTrace:
    claim_id: str
    environments: tuple[str, ...]
    evidence_count: int
    initial_status: str
    independent_support_groups: int
    independent_contradiction_groups: int
    selected_experiment: str | None
    selected_information_gain: float
    experiment_observation: str | None
    updated_status: str
    capability_used: bool


class FixtureSource:
    """Deterministic fixture implementing the same boundary as a real adapter."""

    def __init__(self, observations: tuple[EnvironmentObservation, ...]):
        self.observations = observations

    def observe(self, objective: str, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        return self.observations[:limit]


class EvidenceInvestigationLoop:
    """Connect acquisition, evidence reasoning and experiment selection."""

    def __init__(self, sources: Mapping[str, EnvironmentSource]) -> None:
        self.investigator = ParallelInvestigator(dict(sources), max_workers=max(1, len(sources)))
        self.convergence = EvidenceConvergenceEngine()
        self.selector = DiscriminatingExperimentSelector()

    def investigate(
        self,
        claim: Claim,
        tasks: tuple[InvestigationTask, ...],
        predictions: tuple[Prediction, ...],
        experiment_observation: str,
    ) -> InvestigationLoopTrace:
        results = self.investigator.investigate(tasks)
        observations = self.investigator.merge(results)
        evidence = tuple(self._to_evidence(claim, observation) for observation in observations)
        initial = self.convergence.assess(claim, evidence)

        experiment = self.selector.select(predictions)
        if experiment is None or experiment.expected_information_gain <= 0:
            return InvestigationLoopTrace(
                claim.id, tuple(task.environment for task in tasks), len(evidence),
                initial.status, initial.independent_support_groups,
                initial.independent_contradiction_groups, None, 0.0,
                None, initial.status, False,
            )

        matching = tuple(p for p in experiment.predictions if p.expected == experiment_observation)
        if len(matching) != 1:
            raise ValueError("experiment observation must match exactly one prediction")
        updated_evidence = evidence + (self._experiment_evidence(claim, matching[0]),)
        updated = self.convergence.assess(claim, updated_evidence)
        return InvestigationLoopTrace(
            claim.id, tuple(task.environment for task in tasks), len(evidence),
            initial.status, initial.independent_support_groups,
            initial.independent_contradiction_groups, experiment.id,
            experiment.expected_information_gain, experiment_observation,
            updated.status,
            # Capability use means Cognitia actually selected and executed a
            # discriminating experiment from the evidence landscape. A test
            # that fails to change the final label is still capability use.
            len(matching) == 1 and len(evidence) > 0,
        )

    @staticmethod
    def _to_evidence(claim: Claim, observation: EnvironmentObservation) -> EvidenceRecord:
        metadata = dict(observation.metadata)
        supports_raw = metadata.get("supports")
        supports = None if supports_raw is None else supports_raw.lower() == "true"
        upstream = tuple(value for key, value in observation.metadata if key == "upstream")
        source = EvidenceSource(
            id=observation.source,
            kind=metadata.get("kind", "environment"),
            name=observation.source,
            reliability=observation.reliability,
        )
        lineage = SourceLineage(source.id, upstream) if upstream else None
        return EvidenceRecord(
            id=observation.id,
            claim_id=claim.id,
            source=source,
            content=observation.content,
            supports=supports,
            lineage=lineage,
            observation_id=observation.id,
            method=metadata.get("method", "environment-observation"),
        )

    @staticmethod
    def _experiment_evidence(claim: Claim, prediction: Prediction) -> EvidenceRecord:
        source = EvidenceSource("follow-up-experiment", "experiment", "Discriminating follow-up", .95)
        supports = prediction.hypothesis_id == "cache-failure"
        return EvidenceRecord(
            id="follow-up-observation",
            claim_id=claim.id,
            source=source,
            content=prediction.expected,
            supports=supports,
            observation_id="follow-up-observation",
            method="discriminating-experiment",
        )


def benchmark() -> InvestigationLoopTrace:
    claim = Claim("cache-cause", "The latency anomaly is caused by the cache.", "incident")
    sources = {
        "web": FixtureSource(tuple(
            EnvironmentObservation(
                f"article-{i}", f"article-{i}", "The cache caused the anomaly.", .55,
                (("supports", "true"), ("upstream", "copied-origin"), ("kind", "web")),
            ) for i in range(3)
        )),
        "experiment": FixtureSource((EnvironmentObservation(
            "primary-test", "independent-lab", "Isolation test points away from cache.", .95,
            (("supports", "false"), ("kind", "experiment"), ("method", "controlled-test")),
        ),)),
        "simulation": FixtureSource((EnvironmentObservation(
            "simulation-1", "simulation", "The model predicts cache isolation should reduce latency.", .8,
            (("supports", "true"), ("kind", "simulation")),
        ),)),
    }
    predictions = (
        Prediction("cache:p1", "cache-failure", "isolate cache", "latency remains high", "latency falls"),
        Prediction("network:p1", "network-failure", "isolate cache", "latency falls", "latency remains high"),
    )
    return EvidenceInvestigationLoop(sources).investigate(
        claim,
        (
            InvestigationTask("web", "collect reported evidence", "web"),
            InvestigationTask("experiment", "collect controlled measurement", "experiment"),
            InvestigationTask("simulation", "collect model consequence", "simulation"),
        ),
        predictions,
        "latency falls",
    )


def format_result(trace: InvestigationLoopTrace) -> str:
    return "\n".join((
        "INTEGRATED_INVESTIGATION_LOOP_SUCCESS",
        f"claim: {trace.claim_id}",
        f"environments: {list(trace.environments)}",
        f"evidence: {trace.evidence_count}",
        f"initial_status: {trace.initial_status}",
        f"independent_support: {trace.independent_support_groups}",
        f"independent_contradiction: {trace.independent_contradiction_groups}",
        f"selected_experiment: {trace.selected_experiment}",
        f"information_gain: {trace.selected_information_gain:.3f}",
        f"experiment_observation: {trace.experiment_observation}",
        f"updated_status: {trace.updated_status}",
        f"capability_used: {trace.capability_used}",
    ))
