"""Real internet acquisition for controlled research experiments.

This adapter performs live HTTP requests to Wikimedia's public search API. It
contains no knowledge seeding: returned observations originate from the network
at execution time. The provider remains outside core cognition so network
availability cannot masquerade as intelligence.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

from .environment import EnvironmentObservation
from .web_search import SearchQuery


@dataclass(frozen=True)
class WikimediaSearchProvider:
    """Minimal dependency-free live search provider."""

    endpoint: str = "https://en.wikipedia.org/w/api.php"
    user_agent: str = "Cognitia-research/0.1 (https://github.com/Udene1/Cognitia)"

    def search(self, query: SearchQuery, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        params = urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": " ".join(query.terms),
                "srlimit": min(limit, 50),
                "format": "json",
                "utf8": 1,
            }
        )
        request = urllib.request.Request(
            f"{self.endpoint}?{params}",
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))

        timestamp = datetime.now(timezone.utc).isoformat()
        observations: list[EnvironmentObservation] = []
        for index, item in enumerate(payload.get("query", {}).get("search", [])):
            title = str(item.get("title", ""))
            snippet = str(item.get("snippet", ""))
            page_id = str(item.get("pageid", index))
            observations.append(
                EnvironmentObservation(
                    id=f"web:wikimedia:{page_id}",
                    source="web:wikimedia",
                    content=f"{title}: {snippet}",
                    reliability=0.7,
                    metadata=(
                        ("kind", "search_result"),
                        ("url", f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"),
                        ("page_id", page_id),
                        ("measured_at", timestamp),
                        ("supports", "unknown"),
                        ("query", query.objective),
                    ),
                )
            )
        return tuple(observations)
