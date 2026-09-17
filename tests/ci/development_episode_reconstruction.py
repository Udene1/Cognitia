"""Controlled development-episode experiment using raw repository evidence."""
from __future__ import annotations

import json
import subprocess

from cognitia.development_episode import DevelopmentEpisodeReconstructor
from cognitia.observation import Observation


BEFORE = "b5e84eeefd5655cb132e55cc218c1e89958f9456"
AFTER = "06344584f11887332393202638f78349126d74b0"


def git(*args: str) -> str:
    return subprocess.run(("git", *args), check=True, capture_output=True, text=True).stdout.strip()


def state(commit: str) -> Observation:
    files = tuple(filter(None, git("ls-tree", "-r", "--name-only", commit).splitlines()))
    return Observation.create(
        environment="git",
        kind="repository_state",
        subject=commit,
        payload="\n".join(files),
        source_uri=f"git:{commit}",
        metadata=(("commit", commit), ("tracked_file_count", str(len(files)))),
    )


def main() -> None:
    changed_files = tuple(filter(None, git("diff", "--name-only", BEFORE, AFTER).splitlines()))
    completed = subprocess.run(("python", "-m", "pytest", "tests/test_environment_evidence.py", "-q"), capture_output=True, text=True)
    status = "passed" if completed.returncode == 0 else "failed"
    consequence = Observation.create(
        environment="ci",
        kind="test_result",
        subject="environment-evidence",
        payload=completed.stdout + completed.stderr,
        source_uri="ci:development-episode-reconstruction",
        metadata=(("status", status), ("returncode", str(completed.returncode))),
    )

    episode = DevelopmentEpisodeReconstructor().reconstruct(state(BEFORE), state(AFTER), consequence)
    artifact = {
        "experiment": "development-episode-reconstruction-v1",
        "before": BEFORE,
        "after": AFTER,
        "changed_files": changed_files,
        "consequence_status": status,
        "temporal_relation": episode.temporal_relation,
        "causal_explanation": episode.causal_explanation,
        "interpretation": "The change is observed to precede the test consequence; intended reason is not inferred from this evidence alone.",
    }
    print(json.dumps(artifact, indent=2))
    if completed.returncode:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
