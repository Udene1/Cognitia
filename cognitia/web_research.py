"""Live web research session: search, fetch, and preserve provenance.

This is deliberately an acquisition layer. It does not decide that a page is
true, and it does not contain the answer to the mission. It gives Cognitia
raw observations plus provenance so the evidence subsystem can do the harder
work later.
"""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import urllib.parse
import urllib.request

from .environment import EnvironmentObservation
from .live_web import WikimediaSearchProvider
from .web_search import SearchQuery


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)


@dataclass(frozen=True)
class WebResearchBundle:
    question: str
    search_observations: tuple[EnvironmentObservation, ...]
    document_observations: tuple[EnvironmentObservation, ...]


class LiveWebResearchSession:
    """Acquire a fresh evidence landscape from the live web."""

    def __init__(self, provider: WikimediaSearchProvider | None = None, *, timeout: float = 15.0) -> None:
        self.provider = provider or WikimediaSearchProvider()
        self.timeout = timeout

    def investigate(self, question: str, *, limit: int = 5, fetch_limit: int = 3) -> WebResearchBundle:
        query = SearchQuery(objective=question, terms=tuple(question.split()))
        search_results = self.provider.search(query, limit=limit)
        documents: list[EnvironmentObservation] = []
        for result in search_results[:fetch_limit]:
            metadata = dict(result.metadata)
            url = metadata.get("url")
            if not url:
                continue
            try:
                documents.append(self._fetch(url, result))
            except (OSError, ValueError):
                # Acquisition failures are observations about the environment,
                # not reasons to fabricate or silently substitute content.
                continue
        return WebResearchBundle(question, search_results, tuple(documents))

    def _fetch(self, url: str, search_result: EnvironmentObservation) -> EnvironmentObservation:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "en.wikipedia.org":
            raise ValueError("live fetch is restricted to the configured Wikimedia host")
        request = urllib.request.Request(
            url,
            headers={"User-Agent": self.provider.user_agent, "Accept": "text/html"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            html = response.read().decode("utf-8", errors="replace")
        parser = _TextExtractor()
        parser.feed(html)
        text = " ".join(parser.parts)
        if not text:
            raise ValueError("empty document")
        return EnvironmentObservation(
            id=f"document:{search_result.id}",
            source="web:wikimedia:document",
            content=text[:12000],
            reliability=0.7,
            metadata=(
                ("kind", "web-document"),
                ("url", url),
                ("search_observation", search_result.id),
                ("query", dict(search_result.metadata)["query"]),
            ),
        )
