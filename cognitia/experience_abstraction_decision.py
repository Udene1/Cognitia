"""Research bridge: induced experience abstractions influence future actions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .experience import CognitiveState, EpistemicOutcome, Experience, ExperienceLedger
from .experience_abstraction import ExperienceAbstractionEngine
from .state_action_generation import AvailableOperation, GeneratedAction, StateActionGenerator


@dataclass(frozen=True)
class AbstractionActionAssessment:
    action: GeneratedAction
    score: float
    abstraction_features: tuple[str, ...]
    supporting_experience_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class AbstractionActionDecision:
    selected: AbstractionActionAssessment
    candidates: tuple[AbstractionActionAssessment, ...]
    abstraction: tuple[str, ...]


class AbstractionConditionedActionSelector:
    """Select generated actions from induced abstractions without state IDs."""

    def select(
        self,
        problem: str,
        operations: Sequence[AvailableOperation],
        ledger: ExperienceLedger,
    ) -> AbstractionActionDecision:
        state = CognitiveState(problem)
        generator = StateActionGenerator()
        actions = generator.generate(state, operations, max_actions=max(8, len(operations)))
        engine = ExperienceAbstractionEngine()
        experiences = ledger.all()
        hypotheses = engine.induce(experiences) if experiences else ()
        abstraction = hypotheses[0].features if hypotheses else ()

        assessments: list[AbstractionActionAssessment] = []
        for action in actions:
            score = 0.0
            support: list[str] = []
            contributions: list[str] = []
            for experience in experiences:
                if not hypotheses or not engine.relevant(hypotheses[0], experience):
                    continue
                if not _operation_matches(action.operation.capability, experience.action):
                    continue
                contribution = 0.5 * hypotheses[0].consistency
                if experience.observed.outcome is EpistemicOutcome.REFUTED:
                    contribution *= -1.0
                elif experience.observed.outcome is EpistemicOutcome.PARTIAL:
                    contribution *= 0.5
                support.append(experience.experience_id)
                score += contribution
                contributions.append(f"{experience.experience_id}:{contribution:+.3f}:{experience.observed.outcome.value}")
            assessments.append(AbstractionActionAssessment(
                action=action,
                score=round(score, 6),
                abstraction_features=abstraction,
                supporting_experience_ids=tuple(support),
                rationale="abstraction=" + ("/".join(abstraction) if abstraction else "none") + "; " + (", ".join(contributions) if contributions else "no matching experience"),
            ))

        ranked = tuple(sorted(assessments, key=lambda item: (-item.score, item.action.operation.name, item.action.objective)))
        return AbstractionActionDecision(ranked[0], ranked, abstraction)


def _operation_matches(capability: str, experience_action: str) -> bool:
    return bool(set(capability.lower().replace("-", " ").split()) & set(experience_action.lower().replace("-", " ").split()))
