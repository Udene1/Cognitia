"""Answer sufficiency without hard-coding a particular answer shape."""
from __future__ import annotations

from dataclasses import dataclass
from .language.representation import AnswerContract


@dataclass(frozen=True)
class AnswerPlan:
    contract: AnswerContract
    satisfied_elements: tuple[str, ...]
    missing_elements: tuple[str, ...]
    sufficient: bool
    rationale: str

    @property
    def needs_more_investigation(self) -> bool:
        return not self.sufficient


class AnswerSufficiencyEvaluator:
    """Evaluate whether candidate material satisfies a question's contract."""

    def evaluate(
        self,
        contract: AnswerContract,
        *,
        elements: tuple[str, ...] = (),
        evidence_count: int = 0,
        uncertainty_explicit: bool = False,
        unresolved_gaps: int = 0,
    ) -> AnswerPlan:
        available = set(elements)
        satisfied = tuple(item for item in contract.required_elements if item in available)
        missing = tuple(item for item in contract.required_elements if item not in available)

        evidence_ok = not contract.needs_evidence or evidence_count > 0
        uncertainty_ok = not contract.needs_uncertainty or uncertainty_explicit
        gaps_ok = not unresolved_gaps or contract.answer_kind not in {"yes_no", "quantity", "location", "time_or_event"}
        sufficient = not missing and evidence_ok and uncertainty_ok and gaps_ok

        reasons: list[str] = []
        if missing:
            reasons.append("missing required answer elements")
        if not evidence_ok:
            reasons.append("required evidence is absent")
        if not uncertainty_ok:
            reasons.append("required uncertainty is not explicit")
        if not gaps_ok:
            reasons.append("unresolved gaps prevent a sufficiently bounded direct answer")
        rationale = "answer contract satisfied" if sufficient else "; ".join(reasons)
        return AnswerPlan(contract, satisfied, missing, sufficient, rationale)
