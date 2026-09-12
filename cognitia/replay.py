"""Reconstruct active cognitive state from the durable cognitive journal.

The journal is an append-only record of observations about cognition. Replay is
what turns those records into a current state that can actually influence a
later decision. Replay never treats persisted executable artifacts as trusted
code; candidates remain metadata until an explicit verifier/rehydrator accepts
them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .durable_cognition import DurableCognitiveLedger
from .learning.scientific import Hypothesis, TestResult
from .self_model import CapabilityHistory, CapabilityOutcome


@dataclass
class RecoveredCognitiveState:
    """Current replayed cognitive state plus immutable historical evidence."""

    hypotheses: dict[str, Hypothesis] = field(default_factory=dict)
    capability_history: CapabilityHistory = field(default_factory=CapabilityHistory)
    candidate_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    evaluations: tuple[dict[str, Any], ...] = ()
    builds: tuple[dict[str, Any], ...] = ()
    replayed_events: int = 0

    def hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        return self.hypotheses.get(hypothesis_id)

    def capability_success_rate(self, capability: str) -> float | None:
        return self.capability_history.success_rate(capability)


class CognitiveStateReplayer:
    """Replay durable lifecycle events into a usable cognitive projection."""

    def __init__(self, ledger: DurableCognitiveLedger) -> None:
        self.ledger = ledger

    def replay(self) -> RecoveredCognitiveState:
        state = RecoveredCognitiveState()
        events = self.ledger.journal.all()

        for event in events:
            payload = event.payload
            if event.kind == "hypothesis_state":
                hypothesis = Hypothesis(
                    id=str(payload["id"]),
                    proposition=str(payload["proposition"]),
                    domain=str(payload["domain"]),
                    confidence=float(payload["confidence"]),
                    support_count=int(payload["support_count"]),
                    challenge_count=int(payload["challenge_count"]),
                    inconclusive_count=int(payload["inconclusive_count"]),
                    tested_conditions=tuple(str(v) for v in payload["tested_conditions"]),
                )
                state.hypotheses[hypothesis.id] = hypothesis
            elif event.kind == "hypothesis_test":
                hypothesis_id = str(payload["hypothesis_id"])
                hypothesis = state.hypotheses.get(hypothesis_id)
                if hypothesis is None:
                    raise ValueError(
                        f"hypothesis test {payload.get('id')} references unknown hypothesis {hypothesis_id}"
                    )
                result = TestResult(
                    id=str(payload["id"]),
                    verdict=str(payload["verdict"]),
                    predicted=payload["predicted"],
                    observed=payload["observed"],
                    condition=str(payload["condition"]),
                    reliability=float(payload["reliability"]),
                    explanation=str(payload["explanation"]),
                    tested_at=datetime.fromisoformat(str(payload["tested_at"])),
                )
                state.hypotheses[hypothesis_id] = hypothesis.with_test(result)
            elif event.kind == "capability_outcome":
                outcome = CapabilityOutcome(
                    capability=str(payload["capability"]),
                    successful=bool(payload["successful"]),
                    context=str(payload["context"]),
                    failure_mode=payload["failure_mode"],
                )
                state.capability_history.record(outcome)
            elif event.kind == "candidate_state":
                candidate_id = str(payload["candidate_id"])
                state.candidate_states[candidate_id] = dict(payload)
            elif event.kind == "evaluation":
                state.evaluations = state.evaluations + (dict(payload),)
            elif event.kind == "cognitive_build":
                state.builds = state.builds + (dict(payload),)

        state.replayed_events = len(events)
        return state
