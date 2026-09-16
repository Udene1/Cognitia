"""Generate auditable candidate actions from current cognitive state.

This is an experiment boundary, not a learning architecture. The researcher
provides only the current state and the operations the environment makes
available. Candidate wording is constructed from state variables rather than
from a researcher-authored list of search facets.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .experience import CognitiveState


@dataclass(frozen=True)
class AvailableOperation:
    """An operation the environment permits; it does not encode the desired action."""

    name: str
    capability: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.capability.strip():
            raise ValueError("operation name and capability are required")


@dataclass(frozen=True)
class GeneratedAction:
    operation: AvailableOperation
    objective: str
    source_signals: tuple[str, ...]
    rationale: str


class StateActionGenerator:
    """Construct candidate objectives from state signals and available operations."""

    def generate(
        self,
        state: CognitiveState,
        operations: Sequence[AvailableOperation],
        *,
        max_actions: int = 8,
    ) -> tuple[GeneratedAction, ...]:
        if max_actions < 1:
            raise ValueError("max_actions must be positive")
        if not operations:
            return ()

        signals: list[tuple[str, str]] = []
        if state.uncertainty:
            signals.append(("uncertainty", "reduce unresolved uncertainty"))
        if state.hypothesis_ids:
            signals.append(("hypotheses", "test the current hypotheses"))
        if state.evidence_ids:
            signals.append(("evidence", "check the existing evidence"))
        if state.knowledge_ids:
            signals.append(("knowledge", "verify relevant knowledge"))
        if state.goal:
            signals.append(("goal", f"advance the goal: {state.goal.strip()}"))
        if not signals:
            signals.append(("problem", "acquire information relevant to the problem"))

        generated: list[GeneratedAction] = []
        for operation in operations:
            # The operation supplies only what can be done. The purpose and
            # wording come from the state, so the evaluator cannot hand us a
            # pre-written intermediate search facet.
            for signal_name, purpose in signals:
                objective = f"{operation.capability}: {purpose} for {state.problem.strip()}"
                generated.append(
                    GeneratedAction(
                        operation=operation,
                        objective=objective,
                        source_signals=(signal_name,),
                        rationale=f"State contains {signal_name}; {purpose}.",
                    )
                )
                if len(generated) >= max_actions:
                    return tuple(generated)
        return tuple(generated)
