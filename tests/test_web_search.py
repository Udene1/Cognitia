from cognitia.environment import EnvironmentObservation
from cognitia.web_search import SearchQuery, WebEnvironmentSource


class Provider:
    def search(self, query, *, limit=10):
        assert query.objective == "find evidence"
        assert limit == 2
        return (EnvironmentObservation("r1", "web:test", "evidence"),)


def test_web_environment_delegates_to_provider():
    result = WebEnvironmentSource(Provider()).observe("find evidence", limit=2)
    assert result[0].source == "web:test"
