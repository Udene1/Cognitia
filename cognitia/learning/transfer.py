"""Transfer learned procedures while preventing context-blind generalization."""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from typing import Sequence

from ..capability_acquisition import ReasoningTrace


@dataclass(frozen=True)
class TransferAssessment:
    operation_sequence: tuple[str, ...]
    source_contexts: tuple[str, ...]
    target_context: str
    transferable: bool
    confidence: float
    reason: str


def assess_transfer(traces: Sequence[ReasoningTrace], target_context: str) -> TransferAssessment:
    if not traces:
        raise ValueError("at least one trace is required")
    if not target_context.strip():
        raise ValueError("target context is required")
    sequences = Counter(trace.operations for trace in traces)
    sequence, count = sequences.most_common(1)[0]
    contexts = tuple(sorted({trace.context for trace in traces if trace.context}))
    same_context = all(trace.context == target_context for trace in traces if trace.context)
    transferable = count >= 2 and same_context
    confidence = min(1.0, 0.5 + 0.1 * count) if transferable else 0.25
    reason = (
        "repeated procedure has only been observed within the target context"
        if transferable
        else "procedure has not demonstrated sufficient context stability for transfer"
    )
    return TransferAssessment(sequence, contexts, target_context, transferable, confidence, reason)
