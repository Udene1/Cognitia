from cognitia.memory import Experience, ExperienceStore, Outcome


def test_every_outcome_is_recorded_including_failure() -> None:
    store = ExperienceStore()

    store.record(
        Experience(
            context={"goal": "reduce latency"},
            action="inspect_postgres_locks",
            observation={"waiting_queries": 42},
            outcome=Outcome(
                kind="positive",
                description="Found the likely bottleneck",
                value=0.8,
            ),
        )
    )
    store.record(
        Experience(
            context={"goal": "reduce latency"},
            action="restart_worker",
            observation={"latency_ms": 1200},
            outcome=Outcome(
                kind="negative",
                description="Restart did not reduce latency",
                value=-0.2,
            ),
        )
    )

    experiences = store.all()

    assert len(experiences) == 2
    assert experiences[0].outcome.kind == "positive"
    assert experiences[1].outcome.kind == "negative"
