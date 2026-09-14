from pathlib import Path

from cognitia.durable import DurableEvent, SQLiteCognitiveJournal
from cognitia.memory.ci_state_transport import restore_sqlite_state, snapshot_sqlite_state


def test_sqlite_state_round_trips_through_transport(tmp_path: Path) -> None:
    source = tmp_path / "source"
    archive = tmp_path / "state.tar.gz"
    restored = tmp_path / "restored"

    with SQLiteCognitiveJournal(source / "cognition.sqlite") as journal:
        journal.append(
            DurableEvent(
                id="transport-proof",
                kind="observation",
                source="test",
                payload={"value": 42},
            )
        )

    records = snapshot_sqlite_state(source, archive)
    assert [record.path for record in records] == ["cognition.sqlite"]

    restored_records = restore_sqlite_state(archive, restored)
    assert restored_records == records

    with SQLiteCognitiveJournal(restored / "cognition.sqlite") as journal:
        events = journal.by_kind("observation")
    assert len(events) == 1
    assert events[0].id == "transport-proof"
    assert events[0].payload == {"value": 42}


def test_restore_rejects_tampered_snapshot(tmp_path: Path) -> None:
    source = tmp_path / "source"
    archive = tmp_path / "state.tar.gz"
    restored = tmp_path / "restored"

    with SQLiteCognitiveJournal(source / "cognition.sqlite") as journal:
        journal.append(
            DurableEvent(
                id="tamper-proof",
                kind="observation",
                source="test",
                payload={"value": 1},
            )
        )
    snapshot_sqlite_state(source, archive)

    import tarfile

    tampered = tmp_path / "tampered.tar.gz"
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        with tarfile.open(tampered, "w:gz") as output:
            for member in members:
                extracted = bundle.extractfile(member) if member.isfile() else None
                if member.name == "cognition.sqlite":
                    data = bytearray(extracted.read())
                    data[-1] ^= 0x01
                    import io
                    member.size = len(data)
                    output.addfile(member, io.BytesIO(data))
                elif extracted is not None:
                    output.addfile(member, extracted)
                else:
                    output.addfile(member)

    import pytest

    with pytest.raises(ValueError, match="integrity mismatch"):
        restore_sqlite_state(tampered, restored)
