from cognitia.durable import SQLiteCognitiveJournal
from cognitia.durable_cognition import DurableCognitiveLedger
from cognitia.learning.scientific import Hypothesis, ScientificEvaluator
from cognitia.replay import CognitiveStateReplayer
from cognitia.self_model import CapabilityOutcome


def test_replay_reconstructs_active_hypothesis_and_capability_history(tmp_path):
    path = tmp_path / "cognition.sqlite"
    hypothesis = Hypothesis(
        id="h-replay",
        proposition="the observed effect depends on condition A",
        domain="test",
        confidence=0.6,
    )
    result = ScientificEvaluator().evaluate(
        predicted=True,
        observed=True,
        condition="A",
        reliability=0.9,
    )

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        ledger.record_hypothesis(hypothesis)
        ledger.record_test_result(result, hypothesis_id=hypothesis.id)
        ledger.record_capability_outcome(
            CapabilityOutcome("simulation", True, context="toy model")
        )
        ledger.record_capability_outcome(
            CapabilityOutcome(
                "simulation",
                False,
                context="large model",
                failure_mode="insufficient_precision",
            )
        )

    with SQLiteCognitiveJournal(path) as journal:
        state = CognitiveStateReplayer(DurableCognitiveLedger(journal)).replay()

    recovered = state.hypothesis("h-replay")
    assert recovered is not None
    assert recovered.support_count == 1
    assert recovered.status == "supported"
    assert recovered.tested_conditions == ("A",)
    assert state.capability_success_rate("simulation") == 0.5
    assert state.capability_history.failure_modes("simulation") == (
        "insufficient_precision",
    )
    assert state.replayed_events == 3


def test_replay_does_not_execute_persisted_candidate_code(tmp_path):
    path = tmp_path / "cognition.sqlite"
    from cognitia.capability_acquisition import AcquisitionMode, CapabilityCandidate
    from cognitia.candidate_registry import CandidateRecord, CandidateState

    candidate = CapabilityCandidate(
        name="stored-candidate",
        mode=AcquisitionMode.LEARN_PROCEDURE,
        operations=("aggregate",),
        representation="group_by_reduce",
        source_trace_ids=("trace-1",),
        code_artifact="raise RuntimeError('must never execute')",
    )
    record = CandidateRecord(
        candidate_id="candidate-1",
        candidate=candidate,
        state=CandidateState.HELD,
        benchmark_score=0.8,
        verification_passed=False,
        reason="awaiting rehydration",
    )

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        ledger.record_candidate(record)

    with SQLiteCognitiveJournal(path) as journal:
        state = CognitiveStateReplayer(DurableCognitiveLedger(journal)).replay()

    stored = state.candidate_states["candidate-1"]
    assert stored["candidate"]["executable_rehydration_required"] is True
    assert stored["state"] == "held"
