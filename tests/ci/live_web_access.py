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

assert results, "live web returned no observations"
assert all(item.source == "web:wikimedia" for item in results)
assert all(item.metadata["kind"] == "search_result" for item in results)
assert all(item.metadata["query"] == question for item in results)
assert all(item.metadata["supports"] is None for item in results)
assert any(item.metadata.get("page_id") for item in results)

print("LIVE_WEB_ACQUISITION_SUCCESS")
print(f"QUERY: {question}")
print(f"RESULTS: {len(results)}")
print("ANSWER_SEEDED: False")
print("SOURCE: real Wikimedia network response")
