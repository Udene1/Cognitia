from cognitia.durable import SQLiteCognitiveJournal
from cognitia.durable_cognition import DurableCognitiveLedger
from cognitia.learning.scientific import Hypothesis, ScientificEvaluator
from cognitia.self_model import CapabilityOutcome


def test_hypothesis_and_self_model_evidence_survive_reopen(tmp_path):
    path = tmp_path / "cognition.sqlite"
    hypothesis = Hypothesis(
        id="h-restart",
        proposition="group_by_reduce transfers across compatible schemas",
        domain="code_learning",
        confidence=0.72,
    )
    result = ScientificEvaluator().evaluate(
        predicted={"Ada": 20},
        observed={"Ada": 20},
        condition="held_out_schema",
        reliability=0.95,
        explanation="independent implementation agreed on held-out input",
    )
    updated = hypothesis.with_test(result)
    outcome = CapabilityOutcome(
        capability="group_by_reduce",
        successful=False,
        context="nested schema",
        failure_mode="context_mismatch",
    )

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        ledger.record_hypothesis(updated)
        ledger.record_test_result(result, hypothesis_id=hypothesis.id)
        ledger.record_capability_outcome(outcome)

    with SQLiteCognitiveJournal(path) as journal:
        ledger = DurableCognitiveLedger(journal)
        hypotheses = ledger.hypotheses()
        tests = ledger.hypothesis_tests()
        outcomes = ledger.capability_outcomes()

    assert hypotheses[0]["id"] == "h-restart"
    assert hypotheses[0]["support_count"] == 1
    assert hypotheses[0]["status"] == "supported"
    assert tests[0]["hypothesis_id"] == "h-restart"
    assert tests[0]["reliability"] == 0.95
    assert outcomes[0]["capability"] == "group_by_reduce"
    assert outcomes[0]["failure_mode"] == "context_mismatch"
