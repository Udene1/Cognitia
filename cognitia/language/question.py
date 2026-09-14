"""Question analysis and answer-expectation inference."""
from __future__ import annotations

from dataclasses import dataclass
import re

from .representation import AnswerContract, LanguageFrame, build_language_frame


@dataclass(frozen=True)
class QuestionAnalysis:
    frame: LanguageFrame
    contract: AnswerContract
    question_type: str
    focus: str


def analyze_question(text: str) -> QuestionAnalysis:
    frame = build_language_frame(text, question=True)
    normalized = " ".join(text.strip().split())
    lower = normalized.lower()

    if re.match(r"^(is|are|am|was|were|do|does|did|has|have|had|can|could|will|would|should|shouldn't|isn't|aren't|wasn't|weren't)\b", lower):
        kind = "yes_no"
        required = ("direct answer",)
        # A binary form is expected, but a bare yes/no is not automatically
        # sufficient: causality, uncertainty, or a consequential claim can
        # require the evidence behind the binary conclusion.
        needs_explanation = bool(re.search(r"\b(?:why|because|evidence|prove|certain|safe|reliable|correct|true)\b", lower))
        needs_evidence = needs_explanation or bool(re.search(r"\b(?:true|correct|reliable|safe|works|causes)\b", lower))
        length = "short" if not needs_explanation else "concise_with_reason"
    elif re.match(r"^(who|what)\b", lower):
        kind = "fact_or_identification"
        required = ("identified object or fact",)
        needs_explanation = bool(re.search(r"\b(?:why|how|explain|evidence)\b", lower))
        needs_evidence = bool(re.search(r"\b(?:evidence|according to|source)\b", lower))
        length = "short" if not needs_explanation else "concise_with_reason"
    elif re.match(r"^(when)\b", lower):
        kind = "time_or_event"
        required = ("time or relevant event",)
        needs_explanation = False
        needs_evidence = True
        length = "short"
    elif re.match(r"^(where)\b", lower):
        kind = "location"
        required = ("location",)
        needs_explanation = False
        needs_evidence = False
        length = "short"
    elif re.match(r"^(how many|how much)\b", lower):
        kind = "quantity"
        required = ("quantity",)
        needs_explanation = bool(re.search(r"\b(?:calculate|derive|show|work|why)\b", lower))
        needs_evidence = False
        length = "short" if not needs_explanation else "result_with_work"
    elif re.match(r"^(how)\b", lower):
        kind = "procedure_or_mechanism"
        required = ("mechanism or ordered procedure",)
        needs_explanation = True
        needs_evidence = bool(re.search(r"\b(?:why|evidence|works|true|reliable)\b", lower))
        length = "explanatory"
    elif re.match(r"^(why)\b", lower):
        kind = "explanation_or_cause"
        required = ("causal explanation", "supporting evidence or reasoning", "uncertainty where applicable")
        needs_explanation = True
        needs_evidence = True
        length = "explanatory"
    elif re.match(r"^(compare|contrast)\b", lower) or " vs " in lower or " versus " in lower:
        kind = "comparison"
        required = ("comparison dimensions", "differences", "similarities where relevant")
        needs_explanation = True
        needs_evidence = True
        length = "explanatory"
    elif re.match(r"^(list|name|give me)\b", lower):
        kind = "enumeration"
        required = ("requested items",)
        needs_explanation = bool(re.search(r"\b(?:why|explain|evidence)\b", lower))
        needs_evidence = bool(re.search(r"\b(?:evidence|sources)\b", lower))
        length = "short" if not needs_explanation else "concise_with_reason"
    else:
        kind = "open_ended"
        required = ("answer matching the explicit objective",)
        needs_explanation = True
        needs_evidence = True
        length = "adaptive"

    needs_uncertainty = bool(re.search(r"\b(?:uncertain|likely|possible|could|might|can|prove|certain|reliable)\b", lower)) or kind in {"why", "open_ended"}
    contract = AnswerContract(
        answer_kind=kind,
        requested_length=length,
        needs_explanation=needs_explanation,
        needs_evidence=needs_evidence,
        needs_uncertainty=needs_uncertainty,
        required_elements=required,
    )
    return QuestionAnalysis(frame=frame, contract=contract, question_type=kind, focus=_focus(normalized))


def _focus(text: str) -> str:
    return re.sub(r"^(?:is|are|was|were|do|does|did|has|have|had|can|could|will|would|should|who|what|when|where|why|how(?: many| much)?)\s+", "", text, flags=re.I).rstrip("?").strip()
