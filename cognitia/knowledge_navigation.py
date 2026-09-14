"""Use accumulated knowledge to choose where Cognitia should look first.

Routing is a search prior, never a truth claim. A useful knowledge base should
make investigation cheaper by pointing toward environments that historically
produce useful evidence for similar problems, while preserving the ability to
search elsewhere when the prior fails.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Iterable, Sequence

from .knowledge.model import KnowledgeItem
from .parallel_investigation import InvestigationTask

_TOKEN = re.compile(r"[a-z0-9_]+")


@dataclass(frozen=True)
class RouteExperience:
    """Outcome of trying an environment for an objective."""

    objective: str
    environment: str
    utility: float
    observations: int = 0

    def __post_init__(self) -> None:
        if not self.objective.strip() or not self.environment.strip():
            raise ValueError("objective and environment are required")
        if not 0.0 <= self.utility <= 1.0:
            raise ValueError("utility must be between 0 and 1")
        if self.observations < 0:
            raise ValueError("observations cannot be negative")


@dataclass(frozen=True)
class RouteScore:
    environment: str
    score: float
    prior: float
    learned: float
    knowledge_matches: tuple[str, ...] = ()
    rationale: str = ""


@dataclass
class ResearchRouteMemory:
    """Small deterministic memory of which environments have paid off."""

    experiences: list[RouteExperience] = field(default_factory=list)

    def record(self, experience: RouteExperience) -> None:
        self.experiences.append(experience)

    def score(self, objective: str, environment: str) -> float:
        relevant = [e for e in self.experiences if e.environment == environment]
        if not relevant:
            return 0.0
        tokens = _tokens(objective)
        weighted = []
        for item in relevant:
            overlap = len(tokens & _tokens(item.objective)) / max(1, len(tokens | _tokens(item.objective)))
            weighted.append((item.utility * (0.5 + 0.5 * overlap), item.observations))
        total_weight = sum(1 + min(obs, 10) / 10 for _, obs in weighted)
        return sum(value * (1 + min(obs, 10) / 10) for value, obs in weighted) / total_weight

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = [e.__dict__ for e in self.experiences]
        target.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ResearchRouteMemory":
        target = Path(path)
        if not target.exists():
            return cls()
        raw = json.loads(target.read_text(encoding="utf-8"))
        return cls([RouteExperience(**item) for item in raw])


class KnowledgeGuidedRouter:
    """Rank candidate environments using validated knowledge plus experience."""

    def __init__(self, knowledge: Iterable[KnowledgeItem] = (), *, memory: ResearchRouteMemory | None = None) -> None:
        self.knowledge = tuple(knowledge)
        self.memory = memory or ResearchRouteMemory()

    def rank(self, objective: str, tasks: Sequence[InvestigationTask]) -> tuple[RouteScore, ...]:
        objective_tokens = _tokens(objective)
        results: list[RouteScore] = []
        for task in tasks:
            matches: list[str] = []
            best_prior = 0.0
            for item in self.knowledge:
                text = " ".join((item.subject, item.predicate, str(item.value), item.scope, item.source.kind))
                item_tokens = _tokens(text)
                overlap = len(objective_tokens & item_tokens) / max(1, len(objective_tokens | item_tokens))
                if overlap > 0:
                    best_prior = max(best_prior, overlap * item.source.reliability)
                    if overlap >= 0.25:
                        matches.append(item.id)
            learned = self.memory.score(objective, task.environment)
            score = 0.65 * best_prior + 0.35 * learned
            rationale = "knowledge prior" if best_prior >= learned else "learned route experience"
            if not best_prior and not learned:
                rationale = "unseen route; preserve exploration"
            results.append(RouteScore(task.environment, score, best_prior, learned, tuple(matches), rationale))
        return tuple(sorted(results, key=lambda item: (-item.score, item.environment)))

    def order(self, objective: str, tasks: Sequence[InvestigationTask]) -> tuple[InvestigationTask, ...]:
        scores = {item.environment: item for item in self.rank(objective, tasks)}
        return tuple(sorted(tasks, key=lambda task: (-scores[task.environment].score, task.environment)))

    @staticmethod
    def utility_from_assessment(*, useful_evidence: int, contradiction_discovered: bool, decisive: bool) -> float:
        """Convert investigation outcome into a bounded routing reward."""
        reward = min(0.6, useful_evidence * 0.15)
        if contradiction_discovered:
            reward += 0.2
        if decisive:
            reward += 0.2
        return min(1.0, reward)


def _tokens(value: str) -> set[str]:
    return {token for token in _TOKEN.findall(value.lower()) if len(token) > 2}
