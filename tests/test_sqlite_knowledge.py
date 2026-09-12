from datetime import datetime, timezone

from cognitia.knowledge import KnowledgeItem, KnowledgeSource, SQLiteKnowledgeStore


def make_item() -> KnowledgeItem:
    return KnowledgeItem(
        subject="tradeoff_balance",
        predicate="has_solution_pattern",
        value={
            "logic": [
                "evaluate competing outcomes",
                "hold when improvement carries unresolved regression",
            ],
            "confidence": 0.7,
        },
        source=KnowledgeSource(
            kind="git_source",
            reference="repo:commit:path",
            reliability=1.0,
        ),
        learned_at=datetime(2026, 9, 12, tzinfo=timezone.utc),
        scope="cross_domain_transfer",
    )


def test_sqlite_knowledge_survives_store_recreation(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    item = make_item()

    with SQLiteKnowledgeStore(path) as store:
        store.add(item)

    with SQLiteKnowledgeStore(path) as reopened:
        recovered = reopened.query(subject="tradeoff_balance")

    assert recovered == (item,)


def test_sqlite_query_filters_without_losing_provenance(tmp_path):
    path = tmp_path / "cognitia.sqlite3"
    first = make_item()
    second = KnowledgeItem(
        subject="group_by_reduce",
        predicate="has_solution_pattern",
        value={"logic": ["group", "reduce"]},
        source=KnowledgeSource(kind="test", reference="held-out"),
        scope="code_transfer",
    )

    with SQLiteKnowledgeStore(path) as store:
        store.add(first)
        store.add(second)
        result = store.query(
            predicate="has_solution_pattern", scope="cross_domain_transfer"
        )

    assert result == (first,)
    assert result[0].source.kind == "git_source"
    assert result[0].source.reference == "repo:commit:path"


def test_sqlite_store_rejects_non_serializable_values(tmp_path):
    item = KnowledgeItem(
        subject="invalid",
        predicate="value",
        value={"not_serializable": object()},
        source=KnowledgeSource(kind="test", reference="unit-test"),
    )

    with SQLiteKnowledgeStore(tmp_path / "cognitia.sqlite3") as store:
        try:
            store.add(item)
        except TypeError as exc:
            assert "JSON-serializable" in str(exc)
        else:
            raise AssertionError("non-serializable knowledge must not be persisted")
