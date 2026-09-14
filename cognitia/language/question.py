"""Question analysis and answer-expectation inference."""
from __future__ import annotations

from dataclasses import dataclass, replace
import re

from .representation import AnswerContract, LanguageFrame, build_language_frame


@dataclass(frozen=True)
class QuestionAnalysis:
    frame: LanguageFrame
    contract: AnswerContract
    question_type: str
    focus: str
    requested_operations: tuple[str, ...] = ()
    subquestions: tuple[str, ...] = ()


def analyze_question(text: str) -> QuestionAnalysis:
    frame = build_language_frame(text, question=True)
    normalized = " ".join(text.strip().split())
    lower = normalized.lower()
    subquestions = _subquestions(normalized)

    if re.match(r"^(is|are|am|was|were|do|does|did|has|have|had|can|could|will|would|should|shouldn't|isn't|aren't|wasn't|weren't)\b", lower):
        kind = "yes_no"
        causal_or_consequential = bool(re.search(r"\b(?:why|because|evidence|prove|certain|safe|reliable|correct|true|causes|caused|works|matters|significant|one factor)\b", lower))
        required = ("direct answer", "brief justification") if causal_or_consequential else ("direct answer",)
        needs_explanation = causal_or_consequential
        needs_evidence = bool(re.search(r"\b(?:evidence|prove|certain|reliable|correct|true|causes|caused|safe|works|one factor)\b", lower))
        length = "short_with_justification" if needs_explanation else "short"
        bare = not needs_explanation
        rationale = "A binary result is sufficient unless the wording makes justification necessary." if bare else "A bare binary result would be responsive but insufficient to make the requested claim meaningful or auditable."
        stopping = ("classify the proposition", "stop once the classification is justified")
    elif re.match(r"^(who|what)\b", lower):
        kind = "fact_or_identification"
        required = ("identified object or fact",)
        needs_explanation = bool(re.search(r"\b(?:why|how|explain|evidence)\b", lower))
        needs_evidence = bool(re.search(r"\b(?:evidence|according to|source)\b", lower))
        length = "short" if not needs_explanation else "concise_with_reason"
        bare = not needs_explanation
        rationale = "The requested fact can normally stand as the answer." if bare else "The wording explicitly requests more than identification."
        stopping = ("identify the requested fact or object", "stop when the requested identification is sufficiently supported")
    elif re.match(r"^when\b", lower):
        kind = "time_or_event"
        required = ("time or relevant event",)
        needs_explanation = False; needs_evidence = True; length = "short"; bare = True
        rationale = "The answer target is a temporal fact; supporting evidence is an internal grounding requirement."
        stopping = ("identify the requested time or event", "stop when the temporal claim is sufficiently supported")
    elif re.match(r"^where\b", lower):
        kind = "location"
        required = ("location",)
        needs_explanation = False; needs_evidence = False; length = "short"; bare = True
        rationale = "The requested output is a location."
        stopping = ("identify the location", "stop when the location is resolved")
    elif re.match(r"^(how many|how much)\b", lower):
        kind = "quantity"
        needs_explanation = bool(re.search(r"\b(?:calculate|derive|show|work|why)\b", lower))
        needs_evidence = False; length = "short" if not needs_explanation else "result_with_work"; bare = not needs_explanation
        required = ("quantity",) if bare else ("quantity", "derivation or justification")
        rationale = "The requested output is a quantity." if bare else "The wording requires derivation or justification as well as the quantity."
        stopping = ("derive or identify the quantity", "stop when the result is justified to the required precision")
    elif re.match(r"^how\b", lower):
        kind = "procedure_or_mechanism"
        required = ("mechanism or ordered procedure",)
        needs_explanation = True
        needs_evidence = bool(re.search(r"\b(?:why|evidence|works|true|reliable)\b", lower))
        length = "explanatory"; bare = False
        rationale = "A bare result cannot convey the requested process or mechanism."
        stopping = ("represent the mechanism or procedure", "cover the steps or causal relations necessary to make it understandable")
    elif re.match(r"^why\b", lower):
        kind = "explanation_or_cause"
        required = ("causal explanation", "supporting evidence or reasoning", "uncertainty where applicable")
        needs_explanation = True; needs_evidence = True; length = "explanatory"; bare = False
        rationale = "The question asks for an explanation; listing a cause without its contribution or mechanism is insufficient."
        stopping = ("construct a sufficiently grounded explanation", "account for major supported contributing factors", "state unresolved explanatory gaps")
    elif re.match(r"^(compare|contrast)\b", lower) or " vs " in lower or " versus " in lower:
        kind = "comparison"
        required = ("comparison dimensions", "differences", "similarities where relevant")
        needs_explanation = True; needs_evidence = True; length = "explanatory"; bare = False
        rationale = "A comparison requires explicit dimensions; a bare preference is not a comparison."
        stopping = ("compare the requested candidates on relevant dimensions", "state the resulting distinction or conclusion")
    elif re.match(r"^(list|name|give me)\b", lower):
        kind = "enumeration"
        needs_explanation = bool(re.search(r"\b(?:why|explain|evidence)\b", lower))
        needs_evidence = bool(re.search(r"\b(?:evidence|sources)\b", lower))
        length = "short" if not needs_explanation else "concise_with_reason"; bare = not needs_explanation
        required = ("requested items",) if bare else ("requested items", "brief rationale")
        rationale = "The requested output is an enumeration." if bare else "The wording requests explanation in addition to enumeration."
        stopping = ("cover the requested item set", "stop when the requested scope is satisfied")
    else:
        kind = "open_ended"
        required = ("answer matching the explicit objective",)
        needs_explanation = True; needs_evidence = True; length = "adaptive"; bare = False
        rationale = "Open-ended requests require the system to determine what makes the answer sufficient rather than assuming a fixed length."
        stopping = ("satisfy the explicit objective", "stop when additional investigation is no longer decision-relevant or remaining uncertainty is explicit")

    needs_uncertainty = bool(re.search(r"\b(?:uncertain|likely|possible|could|might|can|prove|certain|reliable|estimate|reported)\b", lower)) or kind in {"explanation_or_cause", "open_ended"}
    contract = AnswerContract(kind, length, needs_explanation, needs_evidence, needs_uncertainty, required, stopping, bare, rationale)
    operations = _operations(kind, lower)
    if len(subquestions) > 1:
        operations = tuple(dict.fromkeys((*operations, "satisfy_all_subquestions")))
    return QuestionAnalysis(
        frame=replace(frame, answer_contract=contract), contract=contract, question_type=kind,
        focus=_focus(normalized), requested_operations=operations, subquestions=subquestions,
    )


def _operations(kind: str, text: str) -> tuple[str, ...]:
    mapping = {
        "yes_no": ("classify_proposition",),
        "fact_or_identification": ("identify_fact_or_object",),
        "time_or_event": ("identify_temporal_fact",),
        "location": ("identify_location",),
        "quantity": ("derive_or_identify_quantity",),
        "procedure_or_mechanism": ("construct_process_or_mechanism",),
        "explanation_or_cause": ("construct_explanation",),
        "comparison": ("compare_candidates",),
        "enumeration": ("construct_enumeration",),
        "open_ended": ("determine_answer_requirements", "retrieve_or_infer_relevant_information"),
    }
    ops = list(mapping[kind])
    if kind == "explanation_or_cause" and any(x in text for x in ("distinguish", "competing", "versus", " vs ")):
        ops.append("compare_explanations")
    if "evidence" in text or "prove" in text:
        ops.append("ground_answer_with_evidence")
    return tuple(dict.fromkeys(ops))


def _subquestions(text: str) -> tuple[str, ...]:
    # Preserve the question clauses; this is intentionally structural, not a claim extractor.
    parts = re.split(r"\s*(?:,\s+and\s+|\s+and\s+|;|\?)\s*", text.strip().rstrip("?"), flags=re.I)
    return tuple(p.strip() + ("?" if p.strip() and not p.strip().endswith("?") else "") for p in parts if p.strip())


def _focus(text: str) -> str:
    return re.sub(r"^(?:is|are|was|were|do|does|did|has|have|had|can|could|will|would|should|who|what|when|where|why|how(?: many| much)?)\s+", "", text, flags=re.I).rstrip("?").strip()
