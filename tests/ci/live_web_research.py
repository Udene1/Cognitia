"""Live search -> source retrieval benchmark with no seeded answer."""
from cognitia.web_research import LiveWebResearchSession

question = "How was the kilogram historically defined and how did its definition change?"
bundle = LiveWebResearchSession().investigate(question, limit=5, fetch_limit=3)

assert bundle.question == question
assert bundle.search_observations
assert all(dict(item.metadata)["query"] == question for item in bundle.search_observations)
assert bundle.document_observations, "live search returned results but no source document could be fetched"
assert all(item.source == "web:wikimedia:document" for item in bundle.document_observations)
assert all(dict(item.metadata)["kind"] == "web-document" for item in bundle.document_observations)
assert all(dict(item.metadata)["search_observation"] for item in bundle.document_observations)

print("LIVE_WEB_RESEARCH_ACQUISITION_SUCCESS")
print(f"QUESTION: {question}")
print(f"SEARCH_RESULTS: {len(bundle.search_observations)}")
print(f"DOCUMENTS_FETCHED: {len(bundle.document_observations)}")
print("ANSWER_SEEDED: False")
print("NEXT_LAYER: evidence qualification and contradiction analysis")
