"""Learn reusable reasoning patterns from observed problem-solving episodes.

Engineering is treated as Cognitia's first experimental environment, not as the
thing Cognitia is ultimately trying to learn.  This module therefore records the
reasoning strategy used in an episode separately from the implementation details
that happened to realize it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from cognitia.memory import Experience


@dataclass(frozen=True)
class ReasoningPattern:
    """Empirical performance of a reasoning strategy in a context."""

    strategy: str
    context: tuple[tuple[str, object], ...]
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

    def matches(self, context: dict[str, object]) -> bool:
        return all(context.get(key) == value for key, value in self.context)


class ReasoningPatternLearner:
    """Learn strategy-level patterns without learning implementation details.

    Experiences opt into reasoning learning by providing a ``reasoning_strategy``
    context field.  This explicit boundary prevents arbitrary commit messages or
    code names from silently becoming claims about Cognitia's reasoning ability.
    """

    strategy_key = "reasoning_strategy"

    def learn(self, experiences: Iterable[Experience]) -> tuple[ReasoningPattern, ...]:
        groups: dict[tuple[str, tuple[tuple[str, object], ...]], list[int]] = {}

        for experience in experiences:
            strategy = experience.context.get(self.strategy_key)
            if not isinstance(strategy, str) or not strategy.strip():
                continue

            context = tuple(
                sorted(
                    (
                        key,
                        value,
                    )
                    for key, value in experience.context.items()
                    if key != self.strategy_key
                )
            )
            key = (strategy, context)
            counts = groups.setdefault(key, [0, 0, 0])
            index = {"positive": 0, "negative": 1, "neutral": 2}[experience.outcome.kind]
            counts[index] += 1

        return tuple(
            ReasoningPattern(
                strategy=strategy,
                context=context,
                positive=counts[0],
                negative=counts[1],
                neutral=counts[2],
            )
            for (strategy, context), counts in sorted(groups.items())
        )

    def applicable(
        self,
        experiences: Iterable[Experience],
        *,
        strategy: str,
        context: dict[str, object],
    ) -> tuple[ReasoningPattern, ...]:
        patterns = self.learn(experiences)
        return tuple(
            pattern
            for pattern in patterns
            if pattern.strategy == strategy and pattern.matches(context)
        )
