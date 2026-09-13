"""Parallel investigation across independent environments and evidence paths."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Iterable, Sequence

from .environment import EnvironmentObservation, EnvironmentSource


@dataclass(frozen=True)
class InvestigationTask:
    id: str
    objective: str
    environment: str


@dataclass(frozen=True)
class InvestigationResult:
    task_id: str
    environment: str
    observations: tuple[EnvironmentObservation, ...]
    error: str | None = None


class ParallelInvestigator:
    """Acquire evidence concurrently without allowing environments to become cognition."""

    def __init__(self, sources: dict[str, EnvironmentSource], *, max_workers: int = 4) -> None:
        if not sources:
            raise ValueError("at least one environment source is required")
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        self.sources = dict(sources)
        self.max_workers = max_workers

    def investigate(self, tasks: Sequence[InvestigationTask], *, limit: int = 10) -> tuple[InvestigationResult, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        def run(task: InvestigationTask) -> InvestigationResult:
            source = self.sources.get(task.environment)
            if source is None:
                return InvestigationResult(task.id, task.environment, (), "environment_unavailable")
            try:
                observations = tuple(source.observe(task.objective, limit))
                return InvestigationResult(task.id, task.environment, observations)
            except Exception as exc:  # environment failures are evidence about capability, not cognition crashes
                return InvestigationResult(task.id, task.environment, (), f"{type(exc).__name__}: {exc}")

        results: dict[str, InvestigationResult] = {}
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(tasks) or 1)) as pool:
            futures = {pool.submit(run, task): task.id for task in tasks}
            for future in as_completed(futures):
                result = future.result()
                results[result.task_id] = result
        return tuple(results[task.id] for task in tasks)

    @staticmethod
    def merge(results: Iterable[InvestigationResult]) -> tuple[EnvironmentObservation, ...]:
        """Merge evidence without declaring conflicting observations resolved."""
        observations: list[EnvironmentObservation] = []
        for result in results:
            observations.extend(result.observations)
        return tuple(observations)
