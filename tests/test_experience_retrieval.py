from cognitia.experience_retrieval import ObservationExperienceRetriever
from cognitia.memory.observation_sqlite import SQLiteObservationStore
from cognitia.observation import Observation


def test_retriever_selects_relevant_observations_without_history_ids(tmp_path):
    store = SQLiteObservationStore(tmp_path / "observations.sqlite")
    try:
        relevant = Observation.create(
            environment="cashflow-os",
            kind="activity.contact",
            subject="contact-1",
            payload='{"leadState":"CONTACTED","channel":"email","outcome":"replied"}',
            observed_at="2026-09-23T01:00:00Z",
        )
        irrelevant = Observation.create(
            environment="cashflow-os",
            kind="inventory.sale",
            subject="sale-1",
            payload='{"product":"yam","quantity":3}',
            observed_at="2026-09-23T01:01:00Z",
        )
        store.ingest(relevant)
        store.ingest(irrelevant)

        matches = ObservationExperienceRetriever().retrieve(
            store,
            "What changed in outreach activity and lead state?",
            environment="cashflow-os",
            limit=5,
        )

        assert matches
        assert matches[0].observation_id == relevant.id
        assert "outreach" in matches[0].matched_terms or "activity" in matches[0].matched_terms
    finally:
        store.close()
