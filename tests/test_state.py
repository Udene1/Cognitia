from cognitia.loop import Decision, cognitive_step
from cognitia.state import Evidence, WorldState


def test_evidence_creates_new_immutable_state():
    state = WorldState()
    evidence = Evidence(
        proposition="postgres_cpu",
        value=94,
        source="monitoring",
        reliability=0.98,
    )

    next_state = state.with_evidence(evidence)

    assert state.version == 0
    assert state.facts == {}
    assert next_state.version == 1
    assert next_state.facts["postgres_cpu"] == 94
    assert next_state.beliefs["postgres_cpu"].confidence == 0.98
    assert next_state.evidence == (evidence,)


def test_reasoner_receives_updated_state():
    observed_versions = []

    def reasoner(state):
        observed_versions.append(state.version)
        return Decision(
            action="inspect_postgres_locks",
            rationale="High CPU requires further evidence.",
        )

    state, decision = cognitive_step(
        WorldState(),
        Evidence(
            proposition="postgres_cpu",
            value=94,
            source="monitoring",
        ),
        reasoner,
    )

    assert observed_versions == [1]
    assert state.facts["postgres_cpu"] == 94
    assert decision.action == "inspect_postgres_locks"
