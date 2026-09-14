"""Deterministic search-strategy planning for open-ended research.

The planner does not answer the question. It constructs bounded information-
seeking actions while preserving the subject of the original question. Search
failures are useful observations: a later learner can use the recorded query,
results, and outcome to improve this planner.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from .web_search import SearchQuery

_TOKEN = re.compile(r"[A-Za-z0-9_]+")
_ENTITY = re.compile(r"\b[A-Z][a-z0-9-]+(?:\s+[A-Z][a-z0-9-]+)+\b")
_STOPWORDS = {
    "why", "what", "when", "where", "who", "which", "how", "did", "does", "do",
    "is", "are", "was", "were", "the", "a", "an", "of", "to", "in", "on", "for",
    "and", "or", "with", "from", "by", "about", "this", "that", "these", "those",
    "evidence", "distinguishes", "distinguish", "competing", "explanations", "explanation",
    "question", "information", "according", "report", "reports", "account", "accounts",
}


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

        core = _topic_terms(objective)
        if not core:
            raise ValueError("objective must contain searchable terms")

        base = " ".join(core)
        actions: list[SearchAction] = [
            SearchAction(SearchQuery(objective=objective, terms=tuple(core)), "direct evidence", 1.0),
        ]
        lowered = objective.lower()
        facets: list[tuple[str, str, float]] = []
        if any(word in lowered for word in ("why", "how", "cause", "causes", "mechanism")):
            facets.append(("mechanism causes", "mechanism", 0.90))
        if any(word in lowered for word in ("history", "historically", "origin", "origins", "changed", "change")):
            facets.append(("history development", "historical development", 0.88))
        # "what evidence" is a request for evidentiary discrimination, not a
        # definition request. The previous planner mistook it for "what is".
        if any(word in lowered for word in ("define", "defined", "definition")) and "what evidence" not in lowered:
            facets.append(("definition terminology", "definition", 0.86))
        if "what evidence" in lowered or "distinguish" in lowered or "competing" in lowered:
            facets.append(("independent evidence competing causes", "independent check", 0.87))
        if any(word in lowered for word in ("current", "today", "now", "latest")):
            facets.append(("current recent", "current status", 0.84))
        if not facets:
            facets = [
                ("definition", "definition", 0.82),
                ("history", "historical context", 0.78),
                ("independent evidence", "independent check", 0.74),
            ]

        for suffix, purpose, priority in facets:
            terms = tuple(_dedupe((*core, *_terms(suffix))))
            actions.append(SearchAction(SearchQuery(objective=f"{base} {suffix}", terms=terms), purpose, priority))

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
        if not unresolved and not contradiction:
            return None
        used = {query.lower().strip() for query in observed_queries}
        candidates = self.plan(objective, max_actions=6).actions
        for action in candidates:
            if action.query.objective.lower() not in used:
                purpose = "contradiction resolution" if contradiction else "uncertainty reduction"
                return SearchAction(action.query, purpose, action.priority + 0.05, parent="adaptive")
        return None


def _topic_terms(value: str) -> list[str]:
    entities = [" ".join(match.group(0).split()) for match in _ENTITY.finditer(value)]
    result: list[str] = []
    covered: set[str] = set()
    for entity in entities:
        result.append(f'"{entity}"')
        covered.update(entity.lower().split())
    for token in [token.lower() for token in _TOKEN.findall(value)]:
        if len(token) <= 2 or token in _STOPWORDS or token in covered:
            continue
        if token not in {item.lower() for item in result}:
            result.append(token)
    return result


def _terms(value: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(value) if len(token) > 2]


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result
