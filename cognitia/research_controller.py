"""Question-driven control over evidence acquisition and answer stopping."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .answer_contract import AnswerAssessment, AnswerContractPlanner, AnswerPlan
from .evidence.landscape import LandscapeDecision
from .language import QuestionAnalysis, analyze_question


@dataclass(frozen=True)
class ResearchState:
    question: str
    analysis: QuestionAnalysis
    plan: AnswerPlan
    landscape: LandscapeDecision | None = None
    answer_elements: tuple[str, ...] = ()
    direct_answer_present: bool = False
    explanation_present: bool = False
    evidence_present: bool = False


@dataclass(frozen=True)
class ResearchAction:
    action: str
    reason: str
    target: str | None
    terminal: bool


class ResearchController:
    """Select what Cognitia still needs without deciding what is true."""

    def __init__(self, planner: AnswerContractPlanner | None = None) -> None:
        self.planner = planner or AnswerContractPlanner()

    def initialize(self, question: str) -> ResearchState:
        analysis = analyze_question(question)
        return ResearchState(question, analysis, self.planner.plan(analysis))

    def update(self, state: ResearchState, *, landscape: LandscapeDecision | None = None,
               answer_elements: Sequence[str] = (), direct_answer_present: bool = False,
               explanation_present: bool = False, evidence_present: bool = False) -> ResearchState:
        return ResearchState(state.question, state.analysis, state.plan, landscape,
                             tuple(answer_elements), direct_answer_present,
                             explanation_present, evidence_present)

    def next_action(self, state: ResearchState) -> ResearchAction:
        assessment: AnswerAssessment = self.planner.assess(
            state.analysis.contract,
            elements=state.answer_elements,
            direct_answer=state.direct_answer_present,
            explanation=state.explanation_present,
            evidence=state.evidence_present,
        )
        if assessment.sufficient and self._can_stop(state.landscape):
            return ResearchAction("stop", "answer contract satisfied and evidence permits stopping", None, True)
        if state.landscape is None:
            return ResearchAction("acquire_evidence", "no evidence landscape exists yet", state.question, False)
        if state.landscape.conclusion == "conflicted":
            target = state.landscape.unresolved_gaps[0].claim_id if state.landscape.unresolved_gaps else None
            return ResearchAction("investigate", "conflicting evidence requires discrimination", target, False)
        if state.landscape.unresolved_gaps:
            return ResearchAction("investigate", "highest-priority evidence gap remains unresolved", state.landscape.unresolved_gaps[0].claim_id, False)
        if assessment.missing_elements:
            return ResearchAction("complete_answer", "required answer element remains missing", assessment.missing_elements[0], False)
        return ResearchAction("acquire_evidence", "current evidence does not yet justify stopping", state.question, False)

    @staticmethod
    def _can_stop(landscape: LandscapeDecision | None) -> bool:
        return bool(landscape and landscape.conclusion == "supported" and not landscape.unresolved_gaps and landscape.confidence > 0)


def initialize_research(question: str) -> ResearchState:
    return ResearchController().initialize(question)
