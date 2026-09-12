from cognitia.build import CapabilityRecord, create_build
from cognitia.capability_acquisition import AcquisitionMode, CapabilityCandidate
from cognitia.candidate_registry import CandidateRecord, CandidateState
from cognitia.cognitive_history import EvaluationRecord, PromotionEvent
from cognitia.durable import SQLiteCognitiveJournal
from cognitia.durable_cognition import DurableCognitiveLedger


def candidate() -> CapabilityCandidate:
    return CapabilityCandidate(
        name="group_by_reduce",
        mode=AcquisitionMode.LEARN_PROCEDURE,
        operations=("group", "reduce"),
        implementation=lambda value: value,
        representation="group records, then reduce values",
        source_trace_ids=("trace-1",),
        code_artifact="def solve(rows): ...",
    )


def test_candidate_evaluation_and_build_survive_reopen(tmp_path):
    path = tmp_path / "cognition.sqlite"
    record = CandidateRecord(candidate_id="cand-1", candidate=candidate())
    evaluation = EvaluationRecord(
        candidate_id="cand-1",
        event=PromotionEvent.BENCHMARKED,
        benchmark_name="held_out_transfer",
        baseline_score=0.5,
        candidate_score=0.9,
    )
    build = create_build(
        "build-7",
        "0.1.0",
        [CapabilityRecord("group_by_reduce", "verified")],
    )

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        ledger.record_candidate(record)
        ledger.record_evaluation(evaluation)
        ledger.record_build(build)

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        snapshots = ledger.candidate_snapshots()
        evaluations = ledger.evaluations()
        builds = ledger.builds()

    assert snapshots[0]["candidate_id"] == "cand-1"
    assert snapshots[0]["candidate"]["code_artifact"] == "def solve(rows): ..."
    assert snapshots[0]["candidate"]["executable_rehydration_required"] is True
    assert evaluations[0]["candidate_score"] == 0.9
    assert builds[0]["build_id"] == "build-7"
    assert builds[0]["capabilities"][0]["name"] == "group_by_reduce"


def test_durable_projection_preserves_hold_and_regression_reason(tmp_path):
    path = tmp_path / "cognition.sqlite"
    record = CandidateRecord(
        candidate_id="cand-regression",
        candidate=candidate(),
        state=CandidateState.HELD,
        benchmark_score=0.7,
        reason="new capability regressed protected benchmark",
    )
    evaluation = EvaluationRecord(
        candidate_id="cand-regression",
        event=PromotionEvent.HELD,
        baseline_score=0.8,
        candidate_score=0.7,
        regression=0.1,
        reason="hold for balancing",
    )

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        ledger.record_candidate(record)
        ledger.record_evaluation(evaluation)

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        snapshot = ledger.candidate_snapshots()[0]
        recovered = ledger.evaluations()[0]

    assert snapshot["state"] == "held"
    assert snapshot["reason"] == "new capability regressed protected benchmark"
    assert recovered["regression"] == 0.1
    assert recovered["reason"] == "hold for balancing"
