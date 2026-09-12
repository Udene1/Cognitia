import os
from pathlib import Path

from cognitia.durable import SQLiteCognitiveJournal
from cognitia.durable_cognition import DurableCognitiveLedger
from cognitia.replay import CognitiveStateReplayer

path = Path(os.environ["COGNITIA_REPLAY_ROOT"]) / "cognition.sqlite"

with SQLiteCognitiveJournal(path) as journal:
    state = CognitiveStateReplayer(DurableCognitiveLedger(journal)).replay()

hypothesis = state.hypothesis("restart-hypothesis")
assert hypothesis is not None
assert hypothesis.status == "challenged"
assert hypothesis.challenge_count == 1
assert state.capability_success_rate("hypothesis_testing") == 0.5
assert state.capability_history.failure_modes("hypothesis_testing") == (
    "insufficient_precision",
)
assert state.replayed_events == 4

# The recovered state is now usable by a later cognitive step rather than
# merely being inspectable storage.
if hypothesis.status == "challenged":
    decision = "seek_new_evidence_or_revise"
else:
    decision = "continue_testing"

assert decision == "seek_new_evidence_or_revise"
print("RECOVERED_HYPOTHESIS_STATUS: challenged")
print("RECOVERED_CAPABILITY_SUCCESS_RATE: 0.5")
print(f"RECOVERED_DECISION: {decision}")
print("ACTIVE_COGNITIVE_REPLAY_SUCCESS")
