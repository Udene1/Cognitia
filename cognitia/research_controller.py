"""Question-driven control over evidence acquisition and answer stopping."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .answer_contract import AnswerAssessment, AnswerContractPlanner, AnswerPlan
from .evidence.landscape import LandscapeDecision, ResearchQuestion
from .language import QuestionAnalysis, analyze_question


@dataclass(frozen=True)
class ResearchState:
    """Minimal state needed to decide whether research should continue."""

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
    """The next action selected from the current research state."""

    action: str
    reason: str
    target: str | None
    terminal: bool


class ResearchController:
    """Turn answer requirements and evidence state into a bounded next action.

    This controller does not decide what is true. It decides what remains necessary
    before Cognitia can legitimately stop, using the question's own answer contract.
    """

    def __init__(self, planner: AnswerContractPlanner | None = None) -> None:
        self.planner = planner or AnswerContractPlanner()

    def initialize(self, question: str) -> ResearchState:
        analysis = analyze_question(question)
        return ResearchState(question=question, analysis=analysis, plan=self.planner.plan(analysis))

    def update(
        self,
        state: ResearchState,
        *,
        landscape: LandscapeDecision | None = None,
        answer_elements: Sequence[str] = (),
        direct_answer_present: bool = False,
        explanation_present: bool = False,
        evidence_present: bool = False,
    ) -> ResearchState:
        return ResearchState(
            question=state.question,
            analysis=state.analysis,
            plan=state.plan,
            landscape=landscape,
            answer_elements=tuple(answer_elements),
            direct_answer_present=direct_answer_present,
            explanation_present=explanation_present,
            evidence_present=evidence_present,
        )

    def next_action(self, state: ResearchState) -> ResearchAction:
        assessment: AnswerAssessment = self.planner.assess(
            state.analysis.contract,
            elements=state.answer_elements,
            direct_answer=state.direct_answer_present,
            explanation=state.explanation_present,
            evidence=state.evidence_present,
        )
        if assessment.sufficient and self._landscape_allows_stop(state.landscape):
            return ResearchAction("stop", "answer contract satisfied and evidence state permits stopping", None, True)

        if state.landscape is None:
            return ResearchAction("acquire_evidence", "no evidence landscape exists yet", state.question, False)

        if state.landscape.next_action:
            return ResearchAction(
                "investigate",
                state.landscape.next_action,
                self._target_from_landscape(state.landscape),
                False,
            )
        if assessment.missing_elements:
            return ResearchAction("complete_answer", "required answer elements remain missing", assessment.missing_elements[0], False)
        return ResearchAction("acquire_evidence", "answer is not yet justified by the current state", state.question, False)

    @staticmethod
    def _landscape_allows_stop(landscape: LandscapeDecision | None) -> bool:
        if landscape is None:
            return False
        return landscape.conclusion == "supported" and not landscape.unresolved_gaps and landscape.confidence > 0

    @staticmethod
    def _target_from_landscape(landscape: LandscapeDecision) -> str | None:
        if landscape.unresolved_gaps:
            return landscape.unresolved_gaps[0].claim_id
        if landscape.contradicting_claims:
            return landscape.contradicting_claims[0]
        if landscape.supporting_claims:
            return landscape.supporting_claims[0]
        return None


def initialize_research(question: str) -> ResearchState:
    return ResearchController().initialize(question)
