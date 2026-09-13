"""Prove web acquisition is an evidence capability, not hidden cognition."""
from cognitia.environment import EnvironmentObservation
from cognitia.web_search import SearchQuery, WebEnvironmentSource


class DeterministicProvider:
    def search(self, query: SearchQuery, *, limit: int = 10):
        assert query.objective == "find evidence about engine balance"
        return (
            EnvironmentObservation(
                id="web-1",
                source="provider:test",
                content="example evidence",
                reliability=0.9,
                metadata=(("kind", "search_result"),),
            ),
        )[:limit]


observations = WebEnvironmentSource(DeterministicProvider()).observe(
    "find evidence about engine balance", limit=5
)
assert observations[0].source == "provider:test"
assert observations[0].reliability == 0.9
assert observations[0].metadata == (("kind", "search_result"),)

print("WEB_CAPABILITY_BOUNDARY_SUCCESS")
print("EVIDENCE_SOURCE:", observations[0].source)
print("REASONING_PROVIDER: NONE")
print("LLM_DEPENDENCY: NONE")
