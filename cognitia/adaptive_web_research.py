"""Adaptive web research: plan queries, acquire observations, and preserve uncertainty."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .evidence.convergence import ConvergenceAssessment, EvidenceConvergenceEngine
from .evidence.model import Claim, EvidenceRecord, EvidenceSource, SourceLineage
from .environment import EnvironmentObservation
from .live_web import WikimediaSearchProvider
from .research_search import ResearchSearchPlanner, SearchAction


@dataclass(frozen=True)
class ResearchRound:
    action: SearchAction
    observations: tuple[EnvironmentObservation, ...]
    evidence: tuple[EvidenceRecord, ...]
    assessment: ConvergenceAssessment


@dataclass(frozen=True)
class AdaptiveResearchTrace:
    question: str
    rounds: tuple[ResearchRound, ...]
    next_action: SearchAction | None
    status: str


class AdaptiveWebResearch:
    """Bounded research loop over a real or injected web environment."""

    def __init__(self, provider: WikimediaSearchProvider | None = None,
                 *, planner: ResearchSearchPlanner | None = None,
                 convergence: EvidenceConvergenceEngine | None = None) -> None:
        self.provider = provider or WikimediaSearchProvider()
        self.planner = planner or ResearchSearchPlanner()
        self.convergence = convergence or EvidenceConvergenceEngine()

    def investigate(self, question: str, *, max_rounds: int = 3,
                    results_per_query: int = 5) -> AdaptiveResearchTrace:
        if max_rounds < 1:
            raise ValueError("max_rounds must be positive")
        if results_per_query < 1:
            raise ValueError("results_per_query must be positive")

        claim = Claim(id="research-question", proposition=question, domain="web-research")
        plan = self.planner.plan(question, max_actions=max_rounds)
        rounds: list[ResearchRound] = []
        observed_queries: list[str] = []
        next_action: SearchAction | None = None

        pending = list(plan.actions)
        while pending and len(rounds) < max_rounds:
            action = pending.pop(0)
            if action.query.objective in observed_queries:
                continue
            observations = self.provider.search(action.query, limit=results_per_query)
            observed_queries.append(action.query.objective)
            evidence = self._as_evidence(claim, observations)
            # Web acquisition deliberately reports unknown polarity. The
            # convergence result therefore measures whether the web boundary
            # supplied qualified support, rather than hallucinating truth.
            assessment = self.convergence.assess(claim, evidence)
            rounds.append(ResearchRound(action, observations, evidence, assessment))

            if assessment.status in {"supported", "contradicted"}:
                next_action = None
                break
            next_action = self.planner.follow_up(
                question,
                observed_queries=observed_queries,
                unresolved=assessment.status in {"unresolved", "no_evidence", "conflicted"},
                contradiction=assessment.status == "conflicted",
            )
            if next_action is not None:
                pending.insert(0, next_action)

        final_status = rounds[-1].assessment.status if rounds else "no_evidence"
        if next_action is not None and next_action.query.objective in observed_queries:
            next_action = None
        return AdaptiveResearchTrace(question, tuple(rounds), next_action, final_status)

    @staticmethod
    def _as_evidence(claim: Claim, observations: Sequence[EnvironmentObservation]) -> tuple[EvidenceRecord, ...]:
        records: list[EvidenceRecord] = []
        for observation in observations:
            metadata = dict(observation.metadata)
            source = EvidenceSource(
                id=observation.source,
                kind=metadata.get("kind", "web"),
                name=observation.source,
                reliability=observation.reliability,
                metadata=metadata,
            )
            records.append(EvidenceRecord(
                id=observation.id,
                claim_id=claim.id,
                source=source,
                content=observation.content,
                supports=None,
                lineage=SourceLineage(observation.source, ()),
                observation_id=observation.id,
                measured_at=metadata.get("measured_at"),
                method="live-web-search",
                metadata=metadata,
            ))
        return tuple(records)
