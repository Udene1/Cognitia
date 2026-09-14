"""Prove that CI acquires observations from the real Internet, not fixtures.

The question is deliberately not accompanied by an expected answer or seeded
source. This first live benchmark proves only acquisition/provenance; later
benchmarks will require Cognitia to construct and validate an answer from the
observations itself.
"""
from cognitia.live_web import WikimediaSearchProvider
from cognitia.web_search import SearchQuery

question = "What is the history of the kilogram?"
query = SearchQuery(objective=question, terms=tuple(question.split()))
results = WikimediaSearchProvider().search(query, limit=5)

metadata = [dict(item.metadata) for item in results]
assert results, "live web returned no observations"
assert all(item.source == "web:wikimedia" for item in results)
assert all(item["kind"] == "search_result" for item in metadata)
assert all(item["query"] == question for item in metadata)
assert all(item["supports"] == "unknown" for item in metadata)
assert any(item.get("page_id") for item in metadata)

print("LIVE_WEB_ACQUISITION_SUCCESS")
print(f"QUERY: {question}")
print(f"RESULTS: {len(results)}")
print("ANSWER_SEEDED: False")
print("SOURCE: real Wikimedia network response")
