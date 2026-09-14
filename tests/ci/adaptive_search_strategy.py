"""CI proof that Cognitia chooses and executes a bounded multi-query search plan."""
from __future__ import annotations

from cognitia.environment import EnvironmentObservation
from cognitia.research_search import ResearchSearchPlanner
from cognitia.adaptive_web_research import AdaptiveWebResearch
from cognitia.web_search import SearchQuery


class RecordingProvider:
    def __init__(self) -> None:
        self.queries: list[SearchQuery] = []

    def search(self, query: SearchQuery, *, limit: int = 10) -> tuple[EnvironmentObservation, ...]:
        self.queries.append(query)
        return tuple(
            EnvironmentObservation(
                id=f"obs:{len(self.queries)}:{index}",
                source="test:web",
                content=f"fresh observation for {query.objective} #{index}",
                reliability=0.6,
                metadata=(("kind", "search_result"), ("query", query.objective), ("supports", "unknown")),
            )
            for index in range(min(limit, 2))
        )


question = "How did the kilogram historically change its definition?"
planner = ResearchSearchPlanner()
plan = planner.plan(question, max_actions=3)
assert len(plan.actions) == 3
assert len({action.query.terms for action in plan.actions}) == 3
assert plan.actions[0].purpose == "direct evidence"
assert any(action.purpose == "mechanism" for action in plan.actions)
assert any(action.purpose == "historical development" for action in plan.actions)

provider = RecordingProvider()
trace = AdaptiveWebResearch(provider=provider, planner=planner).investigate(question, max_rounds=3, results_per_query=2)
assert len(trace.rounds) == 3
assert len(provider.queries) == 3
assert len({query.objective for query in provider.queries}) == 3
assert all(round.assessment.status == "unresolved" for round in trace.rounds)
assert all(record.supports is None for round in trace.rounds for record in round.evidence)
assert trace.next_action is not None or len(trace.rounds) == 3
print("ADAPTIVE_SEARCH_STRATEGY_SUCCESS")
