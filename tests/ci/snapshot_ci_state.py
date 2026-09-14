"""Create the artifact that will cross the ephemeral runner boundary."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.memory.ci_state_transport import snapshot_sqlite_state

root = Path(os.environ["COGNITIA_PERSISTENCE_ROOT"])
archive = Path(os.environ["COGNITIA_STATE_ARCHIVE"])
records = snapshot_sqlite_state(root, archive)
print(f"CI_STATE_SNAPSHOT_SUCCESS: {len(records)} SQLite databases")
for record in records:
    print(f"CI_STATE_SNAPSHOT_DATABASE: {record.path} sha256={record.sha256}")
