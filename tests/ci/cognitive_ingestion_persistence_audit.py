"""Audit what Cognitia actually retains from code and live research.

This is an evidence audit, not a capability fixture. It intentionally reports
what the current implementation does instead of making a missing capability
appear to exist.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path
import tempfile

from cognitia.durable import SQLiteCognitiveJournal
from cognitia.open_research import OpenEndedResearch
from cognitia.web_research import LiveWebResearchSession

ARTIFACT = Path(".ci/cognitive-ingestion-persistence-audit.json")


def main() -> None:
    package_root = Path(__file__).resolve().parents[2] / "cognitia"
    source_files = sorted(str(path.relative_to(package_root.parent)) for path in package_root.rglob("*.py"))

    open_research_source = inspect.getsource(OpenEndedResearch)
    web_source = inspect.getsource(LiveWebResearchSession)
    journal_source = inspect.getsource(SQLiteCognitiveJournal)

    code_ingestion_markers = [
        marker for marker in ("repository", "git", "codebase", "source_file", "CodeObservation")
        if marker in open_research_source or marker in web_source
    ]

    with tempfile.TemporaryDirectory(prefix="cognitia-ingestion-audit-") as directory:
        db_path = Path(directory) / "cognition.sqlite"
        with SQLiteCognitiveJournal(db_path) as journal:
            before = len(journal.all())
            bundle = LiveWebResearchSession().investigate(
                "Roman Empire decline evidence competing explanations",
                limit=3,
                fetch_limit=2,
            )
            after_without_persistence = len(journal.all())
            raw_web_ids = [item.id for item in bundle.search_observations + bundle.document_observations]

    artifact = {
        "experiment": "cognitive-ingestion-persistence-audit-v1",
        "codebase": {
            "repository_python_file_count_seen_by_ci": len(source_files),
            "sample_files": source_files[:20],
            "explicit_code_ingestion_markers_in_research_acquisition_layers": code_ingestion_markers,
            "interpretation": "The CI process can see the checked-out repository, but that filesystem visibility is not Cognitia ingestion. The inspected acquisition/research layers expose web/environment observations, not a repository-code ingestion boundary.",
        },
        "live_web": {
            "search_observations": len(bundle.search_observations),
            "document_observations": len(bundle.document_observations),
            "raw_observation_ids": raw_web_ids,
            "journal_events_before": before,
            "journal_events_after_web_acquisition_without_explicit_append": after_without_persistence,
            "web_acquisition_source_contains_journal_append": ".append(" in web_source,
            "open_research_source_contains_journal_append": ".append(" in open_research_source,
            "interpretation": "Live web acquisition creates EnvironmentObservation objects with source, content, URL/query metadata and provenance, but the acquisition layer does not append those raw observations to SQLiteCognitiveJournal. They remain in the in-process research result unless another layer persists them.",
        },
        "durable_memory": {
            "journal_supports_append_only_events": ".append(" in journal_source and "cognitive_events" in journal_source,
            "interpretation": "The durable journal can persist evidence-bearing events, but capability to persist an event is not evidence that raw web observations or the repository codebase are currently persisted there.",
        },
        "research_conclusion": "Current evidence supports durable retention of promoted research knowledge, but not durable retention of the raw web evidence artifacts themselves, and not a demonstrated Cognitia codebase-ingestion path.",
        "next_boundary": "Build a real evidence archive that persists acquired web observations with provenance before promotion, then build a repository/code ingestion environment source that records code artifacts with commit identity and provenance. Keep both as evidence, not automatic knowledge.",
    }

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
