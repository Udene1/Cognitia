"""Behavioral verification for source-derived computational hypotheses."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class BehavioralVerification:
    """Evidence from executing two candidate implementations on held-out cases."""

    verified: bool
    cases_checked: int
    mismatches: tuple[str, ...] = ()
    epistemic_status: str = "verification"


def verify_equivalent(
    left: Callable[[object], object],
    right: Callable[[object], object],
    cases: Sequence[object],
) -> BehavioralVerification:
    """Test agreement on held-out cases; this is not a universal proof."""
    if not cases:
        raise ValueError("at least one held-out case is required")
    mismatches: list[str] = []
    for index, case in enumerate(cases):
        left_result = left(case)
        right_result = right(case)
        if left_result != right_result:
            mismatches.append(f"case {index}: {left_result!r} != {right_result!r}")
    return BehavioralVerification(
        verified=not mismatches,
        cases_checked=len(cases),
        mismatches=tuple(mismatches),
    )
