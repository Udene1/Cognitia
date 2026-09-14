"""Answer construction and epistemic control for Cognitia.

Research modules determine what the system currently believes. This module is
responsible for turning that state into an explicit candidate answer, checking
that the answer contract is satisfied, exposing uncertainty, and representing
answer revisions when new evidence changes the conclusion.

The implementation is deliberately deterministic and model-independent.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
from typing import Iterable, Sequence

from .answer_contract import AnswerAssessment, AnswerContractPlanner
from .research_synthesis import ResearchSynthesis


@dataclass(frozen=True)
class EpistemicState:
    """What Cognitia knows about the strength and limits of a conclusion."""

    status: str
    confidence: str
    evidence_strength: str
    independent_origin_count: int
    uncertainty: tuple[str, ...]
    limitations: tuple[str, ...]
    verification_required: bool
    capability_limits: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateAnswer:
    """A user-facing answer plus the cognitive state that produced it."""

    question: str
    answer: str
    answer_kind: str
    reasoning: tuple[str, ...]
    evidence: tuple[str, ...]
    uncertainty: tuple[str, ...]
    limitations: tuple[str, ...]
    what_would_change_answer: tuple[str, ...]
    verification_actions: tuple[str, ...]
    epistemic: EpistemicState
    research_status: str
    assessment: AnswerAssessment

    @property
    def sufficient(self) -> bool:
        return self.assessment.sufficient

    def render(self) -> str:
        lines = [self.answer]
        if self.reasoning:
            lines.extend(["", "Why:"])
            lines.extend(f"- {item}" for item in self.reasoning)
        if self.evidence:
            lines.extend(["", "Evidence:"])
            lines.extend(f"- {item}" for item in self.evidence)
        if self.uncertainty:
            lines.extend(["", "Uncertainty:"])
            lines.extend(f"- {item}" for item in self.uncertainty)
        if self.limitations:
            lines.extend(["", "Limitations:"])
            lines.extend(f"- {item}" for item in self.limitations)
        if self.what_would_change_answer:
            lines.extend(["", "What could change this answer:"])
            lines.extend(f"- {item}" for item in self.what_would_change_answer)
        if self.verification_actions:
            lines.extend(["", "Verification:"])
            lines.extend(f"- {item}" for item in self.verification_actions)
        return "\n".join(lines)


@dataclass(frozen=True)
class AnswerRevision:
    """An auditable transition between two answers."""

    previous_fingerprint: str
    new_fingerprint: str
    changed: bool
    changed_because: tuple[str, ...]
    previous_answer: str
    new_answer: str


class AnsweringCore:
    """Construct, validate, and revise answers without requiring an LLM."""

    def __init__(self, planner: AnswerContractPlanner | None = None) -> None:
        self.planner = planner or AnswerContractPlanner()

    def build(
        self,
        synthesis: ResearchSynthesis,
        *,
        capability_limits: Iterable[str] = (),
    ) -> CandidateAnswer:
        plan = self.planner.plan(synthesis.question)
        capability_limits_tuple = tuple(dict.fromkeys(item.strip() for item in capability_limits if item.strip()))
        answer = self._direct_answer(synthesis)
        reasoning = tuple(self._reasoning(synthesis))
        evidence = tuple(self._evidence(synthesis))
        uncertainty = tuple(dict.fromkeys((*synthesis.caveats, *capability_limits_tuple)))
        limitations = tuple(dict.fromkeys(self._limitations(synthesis, capability_limits_tuple)))
        changes = tuple(dict.fromkeys(self._what_would_change(synthesis)))
        verification = tuple(dict.fromkeys(self._verification(synthesis, capability_limits_tuple)))
        epistemic = self._epistemic(synthesis, uncertainty, capability_limits_tuple)
        contract = _contract_from_plan_source(synthesis.question)
        elements = _assessment_elements(contract, answer, reasoning, evidence, uncertainty)
        assessment = self.planner.assess(
            contract,
            elements=elements,
            direct_answer=bool(answer.strip()),
            explanation=bool(reasoning),
            evidence=bool(evidence),
        )
        # An explicit insufficiency state is a hard epistemic boundary. A
        # non-empty bounded answer may still be rendered, but it must never be
        # labelled contract-sufficient when the research structure is empty.
        if synthesis.status == "insufficient_explanatory_structure" and assessment.sufficient:
            assessment = replace(
                assessment,
                sufficient=False,
                stopping_reason="insufficient_explanatory_structure",
            )
        return CandidateAnswer(
            question=synthesis.question,
            answer=answer,
            answer_kind=plan.answer_kind,
            reasoning=reasoning,
            evidence=evidence,
            uncertainty=uncertainty if plan.must_state_uncertainty or uncertainty else (),
            limitations=limitations,
            what_would_change_answer=changes,
            verification_actions=verification,
            epistemic=epistemic,
            research_status=synthesis.status,
            assessment=assessment,
        )

    def revise(
        self,
        previous: CandidateAnswer,
        updated_synthesis: ResearchSynthesis,
        *,
        new_evidence: Sequence[str] = (),
        capability_limits: Iterable[str] = (),
    ) -> tuple[CandidateAnswer, AnswerRevision]:
        updated = self.build(updated_synthesis, capability_limits=capability_limits)
        previous_fp = _fingerprint(previous)
        new_fp = _fingerprint(updated)
        reasons: list[str] = []
        if updated.answer != previous.answer:
            reasons.append("new synthesis changed the candidate conclusion")
        if updated.epistemic.confidence != previous.epistemic.confidence:
            reasons.append("epistemic confidence changed")
        if new_evidence:
            reasons.append(f"new evidence incorporated: {len(new_evidence)} item(s)")
        if not reasons:
            reasons.append("new evidence did not change the current conclusion")
        return updated, AnswerRevision(
            previous_fingerprint=previous_fp,
            new_fingerprint=new_fp,
            changed=previous_fp != new_fp,
            changed_because=tuple(reasons),
            previous_answer=previous.answer,
            new_answer=updated.answer,
        )

    @staticmethod
    def _direct_answer(synthesis: ResearchSynthesis) -> str:
        if not synthesis.factors:
            return (
                f"I cannot currently establish a reliable answer to {synthesis.question} "
                "from the available evidence. My best current conclusion is that the evidence is insufficient."
            )
        question = synthesis.question.strip().rstrip("?")
        factors = synthesis.factors
        if question.lower().startswith(("why ", "what caused ", "what causes ")):
            factor_text = _join_factors(factor.factor for factor in factors)
            return (
                f"{question}? The best current explanation is that {factor_text}. "
                "These factors are supported as candidate contributors, but their relative importance is not yet established."
            )
        if question.lower().startswith("how "):
            mechanism = _join_factors(factor.contribution for factor in factors)
            return f"{question}? The available evidence indicates that {mechanism}."
        if question.lower().startswith(("is ", "are ", "was ", "were ", "did ", "does ", "do ")):
            return (
                f"My best current answer to {question}? is that the proposition is not established categorically; "
                "the available evidence supports only a bounded candidate conclusion."
            )
        return f"My best current answer to {question}? is supported by {len(factors)} candidate evidence-backed factor(s)."

    @staticmethod
    def _reasoning(synthesis: ResearchSynthesis) -> list[str]:
        return [factor.contribution for factor in synthesis.factors]

    @staticmethod
    def _evidence(synthesis: ResearchSynthesis) -> list[str]:
        return [
            f"{factor.factor} ({factor.source_count} source(s), {factor.origin_count} observed origin(s), confidence={factor.confidence})."
            for factor in synthesis.factors
        ]

    @staticmethod
    def _limitations(synthesis: ResearchSynthesis, capability_limits: Sequence[str]) -> list[str]:
        limitations = list(synthesis.caveats)
        if capability_limits:
            limitations.append("The answer is bounded by unavailable capabilities: " + "; ".join(capability_limits))
        return list(dict.fromkeys(limitations))

    @staticmethod
    def _what_would_change(synthesis: ResearchSynthesis) -> list[str]:
        return list(synthesis.next_actions)

    @staticmethod
    def _verification(synthesis: ResearchSynthesis, capability_limits: Sequence[str]) -> list[str]:
        actions = list(synthesis.next_actions)
        if capability_limits:
            actions.append("Acquire or invoke the missing capability, then rerun the relevant investigation.")
        return list(dict.fromkeys(actions))

    @staticmethod
    def _epistemic(synthesis: ResearchSynthesis, uncertainty: Sequence[str], capability_limits: Sequence[str]) -> EpistemicState:
        independent = max((factor.origin_count for factor in synthesis.factors), default=0)
        if synthesis.status == "insufficient_explanatory_structure":
            confidence, strength = "very_low", "insufficient"
        elif synthesis.status.startswith("thin_"):
            confidence, strength = "low", "thin"
        elif any(factor.confidence == "candidate_uncertain" for factor in synthesis.factors):
            confidence, strength = "low", "candidate"
        else:
            confidence, strength = "candidate", "candidate"
        return EpistemicState(
            status="bounded_candidate" if confidence != "very_low" else "insufficient",
            confidence=confidence,
            evidence_strength=strength,
            independent_origin_count=independent,
            uncertainty=tuple(uncertainty),
            limitations=tuple(capability_limits),
            verification_required=bool(uncertainty or capability_limits or confidence != "candidate"),
            capability_limits=tuple(capability_limits),
        )


def _assessment_elements(contract, answer: str, reasoning: Sequence[str], evidence: Sequence[str], uncertainty: Sequence[str]) -> set[str]:
    elements: set[str] = set()
    required = {item.lower() for item in contract.required_elements}
    if "causal explanation" in required and answer.strip() and reasoning:
        elements.add("causal explanation")
    if "supporting evidence or reasoning" in required and (evidence or reasoning):
        elements.add("supporting evidence or reasoning")
    if "uncertainty where applicable" in required and uncertainty:
        elements.add("uncertainty where applicable")
    if "identified object or fact" in required and answer.strip():
        elements.add("identified object or fact")
    if "time or relevant event" in required and answer.strip():
        elements.add("time or relevant event")
    if "location" in required and answer.strip():
        elements.add("location")
    if "quantity" in required and answer.strip():
        elements.add("quantity")
    if "mechanism or ordered procedure" in required and (answer.strip() and reasoning):
        elements.add("mechanism or ordered procedure")
    if "comparison dimensions" in required and reasoning:
        elements.add("comparison dimensions")
    if "differences" in required and reasoning:
        elements.add("differences")
    if "similarities where relevant" in required and reasoning:
        elements.add("similarities where relevant")
    if "requested items" in required and answer.strip():
        elements.add("requested items")
    if "brief rationale" in required and reasoning:
        elements.add("brief rationale")
    if "derivation or justification" in required and reasoning:
        elements.add("derivation or justification")
    if "direct answer" in required and answer.strip():
        elements.add("direct answer")
    if "brief justification" in required and reasoning:
        elements.add("brief justification")
    if "answer matching the explicit objective" in required and answer.strip():
        elements.add("answer matching the explicit objective")
    return elements


def _contract_from_plan_source(question: str):
    from .language import analyze_question
    return analyze_question(question).contract


def _join_factors(values: Iterable[str]) -> str:
    cleaned = [value.strip().rstrip(".") for value in values if value.strip()]
    if not cleaned:
        return "the available evidence does not establish a specific mechanism"
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + ", and " + cleaned[-1]


def _fingerprint(answer: CandidateAnswer) -> str:
    payload = "\n".join((answer.question, answer.answer, *answer.reasoning, *answer.evidence, *answer.uncertainty))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
