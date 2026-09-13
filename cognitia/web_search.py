"""Web evidence boundary.

This module does not perform network access yet. It defines the contract that a
real search provider can implement later. Keeping acquisition behind this
boundary prevents search from becoming hidden intelligence or an LLM wrapper.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .environment import EnvironmentObservation, EnvironmentSource


@dataclass(frozen=True)
class SearchQuery:
    objective: str
    terms: tuple[str, ...]
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.objective.strip() or not self.terms:
            raise ValueError("search objective and terms are required")


class WebSearchProvider(Protocol):
    """Provider boundary; implementation may use an index or live web API."""

    def search(self, query: SearchQuery, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        ...


class WebEnvironmentSource(EnvironmentSource):
    """Expose a provider as an evidence-producing environment source."""

    def __init__(self, provider: WebSearchProvider) -> None:
        self.provider = provider

    def observe(self, objective: str, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        query = SearchQuery(objective=objective, terms=tuple(objective.split()))
        return self.provider.search(query, limit=limit)
