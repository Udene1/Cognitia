import os
from pathlib import Path

from cognitia.durable import SQLiteCognitiveJournal
from cognitia.durable_cognition import DurableCognitiveLedger
from cognitia.learning.scientific import Hypothesis, ScientificEvaluator
from cognitia.self_model import CapabilityOutcome

root = Path(os.environ["COGNITIA_REPLAY_ROOT"])
root.mkdir(parents=True, exist_ok=True)
path = root / "cognition.sqlite"

with SQLiteCognitiveJournal(path) as journal:
    ledger = DurableCognitiveLedger(journal)
    hypothesis = Hypothesis(
        id="restart-hypothesis",
        proposition="a failed prediction should reduce confidence in the tested model",
        domain="cognitive-engineering",
        confidence=0.7,
    )
    ledger.record_hypothesis(hypothesis)
    result = ScientificEvaluator().evaluate(
        predicted="success",
        observed="failure",
        condition="held-out-case",
        reliability=1.0,
        explanation="the prediction did not survive the held-out case",
    )
    ledger.record_test_result(result, hypothesis_id=hypothesis.id)
    ledger.record_capability_outcome(
        CapabilityOutcome("hypothesis_testing", True, context="held-out-case")
    )
    ledger.record_capability_outcome(
        CapabilityOutcome(
            "hypothesis_testing",
            False,
            context="adversarial-case",
            failure_mode="insufficient_precision",
        )
    )

print("REPLAY_WRITER_COMPLETE")
