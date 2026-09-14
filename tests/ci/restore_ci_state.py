"""Restore the durable cognitive snapshot at the start of a fresh runner."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.memory.ci_state_transport import restore_sqlite_state

archive = Path(os.environ["COGNITIA_STATE_ARCHIVE"])
root = Path(os.environ["COGNITIA_PERSISTENCE_ROOT"])

if not archive.exists():
    print("CI_STATE_BOOTSTRAP_REQUIRED")
else:
    records = restore_sqlite_state(archive, root)
    print(f"CI_STATE_RESTORED: {len(records)} SQLite databases")
    for record in records:
        print(f"CI_STATE_DATABASE: {record.path} sha256={record.sha256}")
