"""Failure learning for hypothesis search.

A failed investigation is retained as evidence about search strategy; it does not
silently become evidence that the underlying hypothesis is false.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from typing import Iterable

from .failure_analysis import FailureAnalyzer, FailureClass, FailureObservation


@dataclass(frozen=True)
class DiscoveryFailure:
    hypothesis_id: str
    failure_class: FailureClass
    transform: str
    context: tuple[tuple[str, object], ...] = ()


class DiscoveryFailureLearner:
    """Accumulate bounded evidence about which search transformations fail."""

    def __init__(self) -> None:
        self._successes: dict[str, int] = defaultdict(int)
        self._failures: dict[str, int] = defaultdict(int)

    def record(self, failure: DiscoveryFailure) -> None:
        self._failures[failure.transform] += 1

    def record_success(self, transform: str) -> None:
        if not transform.strip():
            raise ValueError("transform is required")
        self._successes[transform] += 1

    def failure_rate(self, transform: str) -> float:
        total = self._successes[transform] + self._failures[transform]
        return self._failures[transform] / total if total else 0.0

    def penalty(self, transform: str) -> float:
        return min(1.0, self.failure_rate(transform))

    def rank(self, transforms: Iterable[str]) -> tuple[str, ...]:
        return tuple(sorted(set(transforms), key=lambda t: (self.penalty(t), t)))

    @staticmethod
    def diagnose(observation: FailureObservation):
        return FailureAnalyzer().diagnose(observation)
