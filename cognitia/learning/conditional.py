"""Learn context-conditioned action patterns from experience.

The learner intentionally does not label an action globally as good or bad.
It records how an action performed under a particular context signature.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from cognitia.memory import Experience


@dataclass(frozen=True)
class ConditionalPattern:
    """Observed performance of an action for one context signature."""

    action: str
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
        """Return whether all learned context fields match the situation."""
        return all(context.get(key) == value for key, value in self.context)


class ConditionalPatternLearner:
    """Derive non-causal, context-conditioned patterns from experiences."""

    def learn(self, experiences: Iterable[Experience]) -> tuple[ConditionalPattern, ...]:
        groups: dict[tuple[str, tuple[tuple[str, object], ...]], list[int]] = {}

        for experience in experiences:
            context = tuple(sorted(experience.context.items(), key=lambda item: item[0]))
            key = (experience.action, context)
            counts = groups.setdefault(key, [0, 0, 0])
            index = {"positive": 0, "negative": 1, "neutral": 2}[experience.outcome.kind]
            counts[index] += 1

        return tuple(
            ConditionalPattern(
                action=action,
                context=context,
                positive=counts[0],
                negative=counts[1],
                neutral=counts[2],
            )
            for (action, context), counts in sorted(groups.items())
        )

    def applicable(
        self,
        experiences: Iterable[Experience],
        *,
        action: str,
        context: dict[str, object],
    ) -> tuple[ConditionalPattern, ...]:
        """Return learned patterns for an action that match the current context."""
        patterns = self.learn(experiences)
        return tuple(
            pattern
            for pattern in patterns
            if pattern.action == action and pattern.matches(context)
        )
