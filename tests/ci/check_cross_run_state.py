"""Prove that state restored from the previous runner is actually readable."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.durable import SQLiteCognitiveJournal

root = Path(os.environ["COGNITIA_PERSISTENCE_ROOT"])
require_prior = os.environ.get("COGNITIA_REQUIRE_PRIOR_STATE") == "1"

with SQLiteCognitiveJournal(root / "cognition.sqlite") as journal:
    runs = journal.by_kind("ci_state_run")

if require_prior:
    assert runs, "expected cognitive state from an earlier GitHub Actions runner"
    print(f"CI_STATE_CROSS_RUN_RECOVERY_SUCCESS: {len(runs)} prior runs recovered")
else:
    print(f"CI_STATE_BOOTSTRAP_OR_RECOVERY: {len(runs)} prior runs present")
