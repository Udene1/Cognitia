"""First process in the durable-cognition restart proof."""
from __future__ import annotations

import os
from pathlib import Path

from cognitia.build import CapabilityRecord, create_build
from cognitia.capability_acquisition import AcquisitionMode, CapabilityCandidate
from cognitia.candidate_registry import CandidateRecord, CandidateState
from cognitia.cognitive_history import EvaluationRecord, PromotionEvent
from cognitia.durable import DurableEvent, SQLiteCognitiveJournal
from cognitia.durable_cognition import DurableCognitiveLedger
from cognitia.knowledge import SQLiteKnowledgeStore
from cognitia.knowledge.model import KnowledgeItem, KnowledgeSource
from cognitia.memory import Experience, Outcome, SQLiteExperienceStore

root = Path(os.environ["COGNITIA_PERSISTENCE_ROOT"])
root.mkdir(parents=True, exist_ok=True)
run_id = os.environ.get("GITHUB_RUN_ID", "local")
commit_sha = os.environ.get("GITHUB_SHA", "local")

knowledge = KnowledgeItem(
    id="restart-proof-knowledge",
    subject="cognitia",
    predicate="learned_pattern",
    value={"family": "group_by_reduce", "confidence": 0.92},
    source=KnowledgeSource(kind="ci", reference="persistence_writer", reliability=1.0),
    scope="restart_proof",
)
experience = Experience(
    id="restart-proof-experience",
    context={"environment": "engineering", "case": "restart"},
    action="persist_learning",
    observation={"knowledge_id": knowledge.id},
    outcome=Outcome("positive", "survived process boundary"),
)

candidate = CapabilityCandidate(
    name="restart-proof-capability",
    mode=AcquisitionMode.LEARN_PROCEDURE,
    operations=("group", "reduce"),
    implementation=lambda value: value,
    representation="group records, then reduce values",
    source_trace_ids=("restart-trace",),
    code_artifact="restart-proof-artifact",
)
candidate_record = CandidateRecord(
    candidate_id="restart-proof-candidate",
    candidate=candidate,
    state=CandidateState.HELD,
    benchmark_score=0.8,
    reason="protected benchmark regression requires balancing",
)
evaluation = EvaluationRecord(
    candidate_id=candidate_record.candidate_id,
    event=PromotionEvent.HELD,
    baseline_score=0.9,
    candidate_score=0.8,
    regression=0.1,
    reason="hold before promotion",
)
build = create_build(
    "restart-proof-build",
    "0.1.0",
    [CapabilityRecord("restart-proof-capability", "verified", "held")],
)

with SQLiteKnowledgeStore(root / "knowledge.sqlite") as store:
    store.add(knowledge)
with SQLiteExperienceStore(root / "experience.sqlite") as store:
    store.record(experience)
with SQLiteCognitiveJournal(root / "cognition.sqlite") as journal:
    journal.append(
        DurableEvent(
            id="restart-proof-event",
            kind="learning_commit",
            source="ci:persistence_writer",
            payload={"knowledge_id": knowledge.id, "experience_id": experience.id},
        )
    )
    journal.append(
        DurableEvent(
            id=f"ci-state-run:{run_id}",
            kind="ci_state_run",
            source="ci:persistence_writer",
            payload={"run_id": run_id, "commit_sha": commit_sha},
        )
    )
    ledger = DurableCognitiveLedger(journal)

    # Re-running a workflow/job must not turn the same durable lifecycle
    # records into duplicates. This is important once the previous runner's
    # SQLite state has been restored before this process starts.
    if not any(item.get("candidate_id") == candidate_record.candidate_id for item in ledger.candidate_snapshots()):
        ledger.record_candidate(candidate_record)
    if not any(item.get("candidate_id") == evaluation.candidate_id for item in ledger.evaluations()):
        ledger.record_evaluation(evaluation)
    if not any(item.get("build_id") == build.build_id for item in ledger.builds()):
        ledger.record_build(build)

print(f"CI_STATE_RUN_RECORDED: {run_id}")
print("PERSISTENCE_WRITE_SUCCESS")
print("DURABLE_COGNITIVE_LIFECYCLE_WRITE_SUCCESS")
