"""Determine whether a state creates an external-information need.

This is an explicit research mechanism, not a claim of semantic understanding.
It separates the existence of an available web-search operation from the
question of whether the current state gives Cognitia a reason to use it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .experience import CognitiveState


class InformationNeedKind(str, Enum):
    NONE = "none"
    EXTERNAL_EVIDENCE = "external_evidence"
    LOCAL_EVIDENCE = "local_evidence"
    COMPUTATION = "computation"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class InformationNeed:
    kind: InformationNeedKind
    reasons: tuple[str, ...]
    confidence: float


class InformationNeedDetector:
    """Make an auditable first distinction between search and non-search work."""

    _FRESHNESS_TERMS = ("latest", "today", "current", "now", "recent", "as of")
    _COMPUTATION_TERMS = ("calculate", "compute", "convert", "how many", "what is the value")

    def detect(self, state: CognitiveState) -> InformationNeed:
        text = state.problem.lower()
        reasons: list[str] = []

        if any(term in text for term in self._FRESHNESS_TERMS):
            reasons.append("request contains an explicit freshness requirement")
            return InformationNeed(InformationNeedKind.EXTERNAL_EVIDENCE, tuple(reasons), 0.95)

        if any(term in text for term in self._COMPUTATION_TERMS):
            reasons.append("request contains an explicit computation signal")
            return InformationNeed(InformationNeedKind.COMPUTATION, tuple(reasons), 0.90)

        if state.uncertainty:
            reasons.append("state contains unresolved uncertainty")
        if state.evidence_ids:
            reasons.append("state already contains evidence")

        if state.evidence_ids and not state.uncertainty:
            return InformationNeed(InformationNeedKind.NONE, tuple(reasons), 0.80)
        if state.uncertainty:
            return InformationNeed(InformationNeedKind.UNRESOLVED, tuple(reasons), 0.55)
        return InformationNeed(InformationNeedKind.LOCAL_EVIDENCE, tuple(reasons), 0.50)
