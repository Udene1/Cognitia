from cognitia.environment import EnvironmentObservation
from cognitia.environment_http import EnvironmentFeed, HttpEnvironmentSource


class FakeProvider:
    def __init__(self):
        self.calls = []

    def fetch(self, objective, *, limit=10, since=None):
        self.calls.append((objective, limit, since))
        return EnvironmentFeed(
            observations=(
                EnvironmentObservation(
                    id="activity:1",
                    source="environment",
                    content='{"kind":"activity.note"}',
                    metadata=(("kind", "activity.note"), ("interface", "rest-api")),
                ),
            ),
            next_since="2026-09-22T13:00:00+00:00",
        )


def test_http_environment_source_preserves_observations_and_advances_cursor():
    provider = FakeProvider()
    source = HttpEnvironmentSource(provider)

    first = source.observe("understand recent work", limit=5)
    second = source.observe("understand recent work", limit=5)

    assert first[0].id == "activity:1"
    assert dict(first[0].metadata)["kind"] == "activity.note"
    assert provider.calls == [
        ("understand recent work", 5, None),
        ("understand recent work", 5, "2026-09-22T13:00:00+00:00"),
    ]
    assert second[0].content == '{"kind":"activity.note"}'
