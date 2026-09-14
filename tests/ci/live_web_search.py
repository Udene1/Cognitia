"""Live-network benchmark: Cognitia acquires fresh observations from the web."""
import os

from cognitia.live_web import WikimediaSearchProvider
from cognitia.web_search import SearchQuery

if os.environ.get("COGNITIA_LIVE_WEB") != "1":
    raise SystemExit("COGNITIA_LIVE_WEB=1 is required for the live-web benchmark")

query = SearchQuery(
    objective="Newton laws of motion",
    terms=("Newton", "laws", "motion"),
)
results = WikimediaSearchProvider().search(query, limit=3)
assert results, "live search returned no observations"
assert all(item.source == "web:wikimedia" for item in results)
assert all(item.metadata.get("url") for item in results)
assert all(item.metadata.get("measured_at") for item in results)
print(f"LIVE_WEB_SEARCH_SUCCESS results={len(results)}")
for item in results:
    print(item.observation)
