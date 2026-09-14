"""Transfer learned procedures across contexts with explicit evidence gates."""
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
    context_independent: bool = False


def assess_transfer(traces: Sequence[ReasoningTrace], target_context: str) -> TransferAssessment:
    """Assess transfer from repeated structure, not target-context identity.

    A procedure may originate in contexts different from the target. Context is
    treated as an adaptation variable. Transfer is only accepted when the same
    operation structure is repeatedly observed and there is no contradictory
    trace; execution in the target still requires separate verification.
    """
    if not traces:
        raise ValueError("at least one trace is required")
    if not target_context.strip():
        raise ValueError("target context is required")
    sequences = Counter(trace.operations for trace in traces)
    sequence, count = sequences.most_common(1)[0]
    contexts = tuple(sorted({trace.context for trace in traces if trace.context}))
    stable = count >= 2
    distinct_contexts = len({trace.context for trace in traces if trace.context}) >= 2
    confidence = min(1.0, 0.45 + 0.12 * count + (0.08 if distinct_contexts else 0.0)) if stable else 0.2
    if stable and distinct_contexts:
        reason = "repeated operation structure survived multiple source contexts; target execution remains a verification obligation"
    elif stable:
        reason = "repeated operation structure is a transfer candidate; cross-context evidence is still thin"
    else:
        reason = "procedure has not demonstrated sufficient structural repetition for transfer"
    return TransferAssessment(sequence, contexts, target_context, stable, confidence, reason, distinct_contexts)
