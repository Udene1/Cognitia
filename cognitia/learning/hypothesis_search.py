"""Learn which hypothesis-space transformations tend to survive testing."""
from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from typing import Iterable

from ..memory.experience import Experience
from ..discovery_hypotheses import HypothesisTransform


@dataclass(frozen=True)
class SearchStrategy:
    transform: HypothesisTransform
    positive: int
    negative: int
    neutral: int

    @property
    def observations(self) -> int:
        return self.positive + self.negative + self.neutral

    @property
    def success_rate(self) -> float:
        if self.observations == 0:
            return 0.0
        return self.positive / self.observations


class HypothesisSearchLearner:
    """Learn transformation utility from explicit investigation outcomes.

    Experiences must opt in with ``hypothesis_transform``. This prevents
    unrelated actions from being interpreted as discovery strategy evidence.
    """

    def learn(self, experiences: Iterable[Experience]) -> tuple[SearchStrategy, ...]:
        counts: dict[HypothesisTransform, list[int]] = defaultdict(lambda: [0, 0, 0])
        for experience in experiences:
            raw = experience.context.get("hypothesis_transform")
            if raw is None:
                continue
            try:
                transform = HypothesisTransform(raw)
            except ValueError:
                continue
            index = {"positive": 0, "negative": 1, "neutral": 2}[experience.outcome.kind]
            counts[transform][index] += 1

        return tuple(
            SearchStrategy(transform, values[0], values[1], values[2])
            for transform, values in sorted(counts.items(), key=lambda item: item[0].value)
        )

    def rank(self, experiences: Iterable[Experience]) -> tuple[SearchStrategy, ...]:
        strategies = self.learn(experiences)
        return tuple(sorted(strategies, key=lambda item: (-item.success_rate, -item.observations, item.transform.value)))
