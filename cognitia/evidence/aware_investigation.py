"""End-to-end investigation: acquire, qualify, converge, and choose the next test."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ..discovery_experiments import DiscriminatingExperimentSelector, Experiment
from ..environment import EnvironmentObservation, EnvironmentSource
from ..parallel_investigation import InvestigationTask, ParallelInvestigator
from .convergence import ConvergenceAssessment, EvidenceConvergenceEngine
from .model import Claim, EvidenceRecord, EvidenceSource, SourceLineage


@dataclass(frozen=True)
class EvidenceInvestigationTrace:
    claim: Claim
    tasks: tuple[InvestigationTask, ...]
    results: tuple[object, ...]
    evidence: tuple[EvidenceRecord, ...]
    assessment: ConvergenceAssessment
    next_experiment: Experiment | None


class EvidenceAwareInvestigator:
    """Keep acquisition, evidence reasoning, and action selection separate."""

    def __init__(
        self,
        sources: Mapping[str, EnvironmentSource],
        *,
        max_workers: int = 4,
        convergence: EvidenceConvergenceEngine | None = None,
        experiment_selector: DiscriminatingExperimentSelector | None = None,
    ) -> None:
        self.parallel = ParallelInvestigator(dict(sources), max_workers=max_workers)
        self.convergence = convergence or EvidenceConvergenceEngine()
        self.experiment_selector = experiment_selector or DiscriminatingExperimentSelector()

    def investigate(
        self,
        claim: Claim,
        tasks: Sequence[InvestigationTask],
        *,
        experiments: Sequence[Experiment] = (),
        limit: int = 10,
    ) -> EvidenceInvestigationTrace:
        results = self.parallel.investigate(tasks, limit=limit)
        evidence = self._to_evidence(claim, results)
        assessment = self.convergence.assess(claim, evidence)
        next_experiment = self._select_next(assessment, experiments)
        return EvidenceInvestigationTrace(
            claim, tuple(tasks), tuple(results), evidence, assessment, next_experiment
        )

    @staticmethod
    def _to_evidence(claim: Claim, results: Sequence[object]) -> tuple[EvidenceRecord, ...]:
        records: list[EvidenceRecord] = []
        for result in results:
            for observation in getattr(result, "observations", ()):
                assert isinstance(observation, EnvironmentObservation)
                metadata = dict(observation.metadata)
                polarity = metadata.get("supports")
                supports = None if polarity is None else polarity.lower() == "true"
                source = EvidenceSource(
                    id=observation.source,
                    kind=metadata.get("kind", "environment"),
                    name=observation.source,
                    reliability=observation.reliability,
                    metadata=metadata,
                )
                upstream = tuple(filter(None, metadata.get("upstream_ids", "").split(",")))
                records.append(EvidenceRecord(
                    id=observation.id,
                    claim_id=claim.id,
                    source=source,
                    content=observation.content,
                    supports=supports,
                    lineage=SourceLineage(observation.source, upstream),
                    observation_id=observation.id,
                    measured_at=metadata.get("measured_at"),
                    method=metadata.get("method"),
                    metadata=metadata,
                ))
        return tuple(records)

    def _select_next(self, assessment: ConvergenceAssessment, experiments: Sequence[Experiment]) -> Experiment | None:
        if not experiments or assessment.status not in {"conflicted", "unresolved", "supported", "contradicted"}:
            return None
        return self.experiment_selector.select(experiments)
