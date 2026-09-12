"""Minimal observe -> update -> reason loop for Cognitia v0.01."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .state import Evidence, WorldState


@dataclass(frozen=True)
class Decision:
    """A proposed action produced from the current state."""

    action: str
    rationale: str


Reasoner = Callable[[WorldState], Decision]


def observe_and_update(state: WorldState, evidence: Evidence) -> WorldState:
    """Advance the world state with a new observation."""
    return state.with_evidence(evidence)


def reason(state: WorldState, reasoner: Reasoner) -> Decision:
    """Ask the reasoning boundary to choose the next action."""
    return reasoner(state)


def cognitive_step(
    state: WorldState,
    evidence: Evidence,
    reasoner: Reasoner,
) -> tuple[WorldState, Decision]:
    """Run one complete v0.01 cognitive transition.

    New evidence changes the immutable state first; only then does the
    reasoner receive that new state. This ordering is intentional.
    """
    next_state = observe_and_update(state, evidence)
    decision = reason(next_state, reasoner)
    return next_state, decision
