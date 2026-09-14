"""Answer planning and sufficiency checks driven by a question's answer contract."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .language import AnswerContract, QuestionAnalysis, analyze_question


@dataclass(frozen=True)
class AnswerAssessment:
    """Whether a candidate structured answer satisfies the requested answer shape."""

    sufficient: bool
    missing_elements: tuple[str, ...]
    satisfied_elements: tuple[str, ...]
    direct_answer_present: bool
    explanation_present: bool
    evidence_present: bool
    recommended_length: str
    stopping_reason: str


@dataclass(frozen=True)
class AnswerPlan:
    """A language-independent plan for rendering a final response."""

    answer_kind: str
    sections: tuple[str, ...]
    requested_length: str
    needs_evidence: bool
    must_state_uncertainty: bool
    stop_when: tuple[str, ...]


class AnswerContractPlanner:
    """Translate question semantics into a rendering-independent answer plan."""

    def plan(self, question: str | QuestionAnalysis) -> AnswerPlan:
        analysis = question if isinstance(question, QuestionAnalysis) else analyze_question(question)
        contract = analysis.contract
        sections = self._sections(contract)
        return AnswerPlan(
            answer_kind=contract.answer_kind,
            sections=sections,
            requested_length=contract.requested_length,
            needs_evidence=contract.needs_evidence,
            must_state_uncertainty=contract.uncertainty_allowed and ("uncertainty" in contract.required_elements or contract.needs_evidence),
            stop_when=contract.stopping_conditions,
        )

    def assess(
        self,
        contract: AnswerContract,
        *,
        elements: Iterable[str] = (),
        direct_answer: bool = False,
        explanation: bool = False,
        evidence: bool = False,
    ) -> AnswerAssessment:
        supplied = {item.strip().lower() for item in elements if item.strip()}
        required = tuple(contract.required_elements)
        satisfied = tuple(item for item in required if item.lower() in supplied)
        missing = tuple(item for item in required if item.lower() not in supplied)
        direct_ok = direct_answer or not contract.direct_answer_required
        explanation_ok = explanation or not contract.needs_explanation
        evidence_ok = evidence or not contract.needs_evidence
        sufficient = not missing and direct_ok and explanation_ok and evidence_ok
        reasons = []
        if not direct_ok: reasons.append("direct_answer_missing")
        if not explanation_ok: reasons.append("explanation_missing")
        if not evidence_ok: reasons.append("evidence_missing")
        if missing: reasons.append("required_elements_missing")
        return AnswerAssessment(
            sufficient=sufficient,
            missing_elements=missing,
            satisfied_elements=satisfied,
            direct_answer_present=direct_answer,
            explanation_present=explanation,
            evidence_present=evidence,
            recommended_length=contract.requested_length,
            stopping_reason="contract_satisfied" if sufficient else ";".join(reasons),
        )

    @staticmethod
    def _sections(contract: AnswerContract) -> tuple[str, ...]:
        if contract.answer_kind == "yes_no":
            return ("direct_answer",)
        if contract.answer_kind in {"fact_or_date", "location", "person_or_agent", "definition_or_fact"}:
            return ("direct_answer", "brief_context")
        sections = ["direct_answer", "explanation"]
        if contract.needs_evidence:
            sections.append("evidence")
        if "uncertainty" in contract.required_elements:
            sections.append("uncertainty")
        return tuple(sections)


def plan_answer(question: str) -> AnswerPlan:
    return AnswerContractPlanner().plan(question)
