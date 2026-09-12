from cognitia.knowledge import KnowledgeStore
from cognitia.knowledge.ingestion import teach


def test_teaching_preserves_provenance_and_scope() -> None:
    store = KnowledgeStore()

    item = teach(
        store,
        subject="postgresql",
        predicate="supports",
        value="locking",
        source_kind="documentation",
        source_reference="postgresql-docs",
        reliability=0.98,
        scope="general",
    )

    assert item.source.reference == "postgresql-docs"
    assert item.source.reliability == 0.98
    assert item.scope == "general"


def test_structured_query_retrieves_relevant_knowledge() -> None:
    store = KnowledgeStore()
    teach(
        store,
        subject="postgresql",
        predicate="supports",
        value="locking",
        source_kind="documentation",
        source_reference="postgresql-docs",
    )
    teach(
        store,
        subject="redis",
        predicate="supports",
        value="streams",
        source_kind="documentation",
        source_reference="redis-docs",
    )

    results = store.query(subject="postgresql", predicate="supports")

    assert len(results) == 1
    assert results[0].value == "locking"
