"""HTTP-backed environment source.

The transport is deliberately generic: the source knows how to retrieve an
environment observation feed, but it does not interpret the environment or
encode application-specific semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .environment import EnvironmentObservation, EnvironmentSource


@dataclass(frozen=True)
class EnvironmentFeed:
    observations: tuple[EnvironmentObservation, ...]
    next_since: str | None = None


class EnvironmentFeedProvider:
    def fetch(self, objective: str, *, limit: int = 10, since: str | None = None) -> EnvironmentFeed:
        raise NotImplementedError


class HttpEnvironmentFeedProvider(EnvironmentFeedProvider):
    def __init__(
        self,
        url: str,
        *,
        opener: Callable[..., object] = urlopen,
        timeout: float = 15.0,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        if not url.strip():
            raise ValueError("environment feed URL is required")
        self.url = url
        self._opener = opener
        self.timeout = timeout
        self.headers = {"accept": "application/json", **(headers or {})}

    def fetch(self, objective: str, *, limit: int = 10, since: str | None = None) -> EnvironmentFeed:
        if limit < 1:
            raise ValueError("limit must be positive")
        params = {"objective": objective, "limit": str(limit)}
        if since:
            params["since"] = since
        separator = "&" if "?" in self.url else "?"
        request = Request(
            f"{self.url}{separator}{urlencode(params)}",
            headers=dict(self.headers),
            method="GET",
        )
        try:
            with self._opener(request, timeout=self.timeout) as response:
                raw = response.read()
        except Exception as exc:
            raise RuntimeError("environment observation request failed") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
            observations = tuple(
                EnvironmentObservation(
                    id=str(item["id"]),
                    source=str(item["source"]),
                    content=str(item["content"]),
                    reliability=float(item.get("reliability", 1.0)),
                    metadata=tuple(
                        (str(key), str(value))
                        for key, value in item.get("metadata", {}).items()
                    ),
                )
                for item in payload.get("observations", [])
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError("invalid environment observation response") from exc
        return EnvironmentFeed(observations=observations, next_since=payload.get("nextSince"))


class HttpEnvironmentSource(EnvironmentSource):
    def __init__(self, provider: EnvironmentFeedProvider) -> None:
        self.provider = provider
        self._since: str | None = None

    def observe(self, objective: str, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        feed = self.provider.fetch(objective, limit=limit, since=self._since)
        self._since = feed.next_since or self._since
        return feed.observations
