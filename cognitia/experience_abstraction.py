"""Induce and revise candidate structural abstractions from experience surfaces.

This experiment deliberately ignores researcher-supplied hypothesis/evidence IDs.
It extracts candidate structural signals from the observed problem surface, keeps
multiple abstraction hypotheses, and revises their support from verified outcomes.
It is a research mechanism, not a claim of semantic understanding.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence

from .experience import EpistemicOutcome, Experience
from .language.representation import LanguageFrame, build_language_frame


@dataclass(frozen=True)
class AbstractionHypothesis:
    features: tuple[str, ...]
    positive: int = 0
    negative: int = 0
    neutral: int = 0

    @property
    def observations(self) -> int:
        return self.positive + self.negative + self.neutral

    @property
    def consistency(self) -> float:
        return (self.positive - self.negative) / self.observations if self.observations else 0.0


@dataclass(frozen=True)
class AbstractedExperience:
    experience_id: str
    features: tuple[str, ...]
    frame_summary: tuple[str, ...]


class ExperienceAbstractionEngine:
    """Generate bounded abstraction hypotheses and revise them from outcomes."""

    FEATURE_FAMILIES = (
        "question",
        "causal",
        "temporal",
        "uncertain",
        "negated",
        "entity",
        "relation_count",
    )

    def abstract(self, experience: Experience) -> AbstractedExperience:
        frame = build_language_frame(experience.prior_state.problem)
        features = self._features(frame)
        return AbstractedExperience(experience.experience_id, features, self._summary(frame))

    def induce(self, experiences: Sequence[Experience]) -> tuple[AbstractionHypothesis, ...]:
        observations = tuple(self.abstract(item) for item in experiences)
        hypotheses: list[AbstractionHypothesis] = []
        for size in range(1, min(3, len(self.FEATURE_FAMILIES)) + 1):
            for family in combinations(self.FEATURE_FAMILIES, size):
                hypotheses.append(self._evaluate(family, observations, experiences))
        return tuple(sorted(hypotheses, key=lambda item: (-item.consistency, -item.observations, item.features)))

    def revise(self, hypotheses: Sequence[AbstractionHypothesis], experience: Experience) -> tuple[AbstractionHypothesis, ...]:
        abstracted = self.abstract(experience)
        revised: list[AbstractionHypothesis] = []
        for hypothesis in hypotheses:
            if not set(hypothesis.features).issubset(set(abstracted.features)):
                revised.append(hypothesis)
                continue
            if experience.observed.outcome is EpistemicOutcome.CONFIRMED:
                revised.append(AbstractionHypothesis(hypothesis.features, hypothesis.positive + 1, hypothesis.negative, hypothesis.neutral))
            elif experience.observed.outcome is EpistemicOutcome.REFUTED:
                revised.append(AbstractionHypothesis(hypothesis.features, hypothesis.positive, hypothesis.negative + 1, hypothesis.neutral))
            else:
                revised.append(AbstractionHypothesis(hypothesis.features, hypothesis.positive, hypothesis.negative, hypothesis.neutral + 1))
        return tuple(sorted(revised, key=lambda item: (-item.consistency, -item.observations, item.features)))

    def relevant(self, hypothesis: AbstractionHypothesis, experience: Experience) -> bool:
        return set(hypothesis.features).issubset(set(self.abstract(experience).features))

    @staticmethod
    def _features(frame: LanguageFrame) -> tuple[str, ...]:
        features = [
            "question" if frame.question else "statement",
            "causal" if frame.causal_relations else "non_causal",
            "temporal" if frame.temporal_markers else "non_temporal",
            "uncertain" if frame.modality else "certain",
            "negated" if frame.negated else "affirmed",
            f"entity:{len(frame.entities)}",
            f"relation_count:{len(frame.relations)}",
        ]
        return tuple(features)

    @staticmethod
    def _summary(frame: LanguageFrame) -> tuple[str, ...]:
        return (
            f"question={frame.question}",
            f"causal_relations={len(frame.causal_relations)}",
            f"temporal_markers={len(frame.temporal_markers)}",
            f"entities={len(frame.entities)}",
            f"relations={len(frame.relations)}",
        )

    def _evaluate(
        self,
        family: Iterable[str],
        observations: Sequence[AbstractedExperience],
        experiences: Sequence[Experience],
    ) -> AbstractionHypothesis:
        features = tuple(family)
        positive = negative = neutral = 0
        for observation, experience in zip(observations, experiences):
            if not set(features).issubset(set(observation.features)):
                continue
            if experience.observed.outcome is EpistemicOutcome.CONFIRMED:
                positive += 1
            elif experience.observed.outcome is EpistemicOutcome.REFUTED:
                negative += 1
            else:
                neutral += 1
        return AbstractionHypothesis(features, positive, negative, neutral)
