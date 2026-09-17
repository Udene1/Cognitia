from cognitia.development_episode import DevelopmentEpisodeReconstructor
from cognitia.observation import Observation


def repository_state(commit: str, files: tuple[str, ...]) -> Observation:
    return Observation.create(
        environment="git",
        kind="repository_state",
        subject=commit,
        payload="\n".join(files),
        source_uri=f"git:{commit}",
        metadata=(("commit", commit), ("tracked_file_count", str(len(files)))),
    )


def consequence(status: str) -> Observation:
    return Observation.create(
        environment="ci",
        kind="test_result",
        subject="environment-evidence",
        payload=status,
        source_uri="ci:test",
        metadata=(("status", status),),
    )


def test_reconstructs_change_before_consequence_without_inventing_reason():
    before = repository_state("state-a", ("cognitia/observation.py",))
    after = repository_state("state-b", ("cognitia/observation.py", "cognitia/development_episode.py"))

    episode = DevelopmentEpisodeReconstructor().reconstruct(
        before,
        after,
        consequence("passed"),
    )

    assert episode.changed is True
    assert episode.temporal_relation == "change_precedes_consequence"
    assert episode.causal_explanation is None


def test_same_state_does_not_create_change_relation():
    state = repository_state("state-a", ("cognitia/observation.py",))

    episode = DevelopmentEpisodeReconstructor().reconstruct(
        state,
        state,
        consequence("passed"),
    )

    assert episode.changed is False
    assert episode.temporal_relation == "no_change_observed"
    assert episode.causal_explanation is None
