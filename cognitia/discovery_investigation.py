"""Discovery investigation loop using environment evidence, not external intelligence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .discovery import ExplanatoryGap
from .environment import EnvironmentObservation, EnvironmentSource
from .web_evidence import EvidenceAssessment, WebEvidenceEvaluator


@dataclass(frozen=True)
class InvestigationResult:
    objective: str
    observations: tuple[EnvironmentObservation, ...]
    assessments: tuple[EvidenceAssessment, ...]
    accepted: tuple[EnvironmentObservation, ...]
    epistemic_status: str = "evidence_acquired"


class DiscoveryInvestigator:
    """Acquire and qualify evidence for an explanatory gap.

    The environment returns observations. Cognitia remains responsible for
    interpretation, hypothesis revision and deciding what the evidence means.
    """

    def __init__(self, source: EnvironmentSource, evaluator: WebEvidenceEvaluator | None = None) -> None:
        self.source = source
        self.evaluator = evaluator or WebEvidenceEvaluator()

    def investigate(self, gap: ExplanatoryGap, *, limit: int = 10) -> InvestigationResult:
        if limit < 1:
            raise ValueError("limit must be positive")
        objective = self._objective(gap)
        observations = tuple(self.source.observe(objective, limit=limit))
        assessments = self.evaluator.assess(observations)
        accepted = tuple(item.observation for item in assessments if item.accepted)
        return InvestigationResult(objective, observations, assessments, accepted)

    @staticmethod
    def _objective(gap: ExplanatoryGap) -> str:
        return "investigate explanatory gap: " + gap.missing_aspect
