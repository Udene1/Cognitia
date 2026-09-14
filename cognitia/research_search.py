"""Deterministic search-strategy planning for open-ended research.

The planner does not answer the question. It constructs a small set of
independent information-seeking actions from the objective, records why each
query was selected, and leaves truth assessment to the evidence subsystem.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from .web_search import SearchQuery

_TOKEN = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class SearchAction:
    query: SearchQuery
    purpose: str
    priority: float
    parent: str | None = None


@dataclass(frozen=True)
class SearchPlan:
    objective: str
    actions: tuple[SearchAction, ...]


class ResearchSearchPlanner:
    """Turn an unfamiliar objective into bounded, auditable search actions."""

    def plan(self, objective: str, *, max_actions: int = 4) -> SearchPlan:
        if not objective.strip():
            raise ValueError("objective is required")
        if max_actions < 1:
            raise ValueError("max_actions must be positive")

        core = _terms(objective)
        if not core:
            raise ValueError("objective must contain searchable terms")

        base = " ".join(core)
        actions: list[SearchAction] = [
            SearchAction(SearchQuery(objective=objective, terms=tuple(core)), "direct evidence", 1.0),
        ]
        lowered = objective.lower()
        facets: list[tuple[str, str, float]] = []
        if any(word in lowered for word in ("why", "how", "cause", "causes", "mechanism")):
            facets.append(("mechanism causes explanation", "mechanism", 0.90))
        if any(word in lowered for word in ("history", "historically", "origin", "origins", "changed", "change")):
            facets.append(("history origin changes", "historical development", 0.88))
        if any(word in lowered for word in ("what", "define", "defined", "definition")):
            facets.append(("definition measurement terminology", "definition", 0.86))
        if any(word in lowered for word in ("current", "today", "now", "latest")):
            facets.append(("current status recent evidence", "current status", 0.84))
        if not facets:
            facets = [
                ("definition measurement", "definition", 0.82),
                ("history development", "historical context", 0.78),
                ("independent evidence disagreement", "independent check", 0.74),
            ]

        for suffix, purpose, priority in facets:
            terms = tuple(_dedupe((*core, *_terms(suffix))))
            actions.append(SearchAction(SearchQuery(objective=f"{base} {suffix}", terms=terms), purpose, priority))

        # Never emit duplicate term sets; preserving order makes traces reproducible.
        unique: list[SearchAction] = []
        seen: set[tuple[str, ...]] = set()
        for action in sorted(actions, key=lambda item: (-item.priority, item.query.terms)):
            if action.query.terms in seen:
                continue
            seen.add(action.query.terms)
            unique.append(action)
            if len(unique) == max_actions:
                break
        return SearchPlan(objective, tuple(unique))

    def follow_up(self, objective: str, *, observed_queries: Sequence[str], unresolved: bool,
                  contradiction: bool) -> SearchAction | None:
        """Choose one next query without pretending the current landscape is settled."""
        if not unresolved and not contradiction:
            return None
        used = {query.lower().strip() for query in observed_queries}
        candidates = self.plan(objective, max_actions=6).actions
        for action in candidates:
            if action.query.objective.lower() not in used:
                purpose = "contradiction resolution" if contradiction else "uncertainty reduction"
                return SearchAction(action.query, purpose, action.priority + 0.05, parent="adaptive")
        return None


def _terms(value: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(value) if len(token) > 2]


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
