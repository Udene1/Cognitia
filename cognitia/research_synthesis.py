"""Grounded multi-factor explanatory synthesis.

This module constructs an auditable explanatory structure from candidate claims.
It does not treat different factor domains as competing explanations merely
because they are different. Multiple factors may jointly contribute to one
outcome; competition requires explicit contrary evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Sequence

from .document_claims import ExtractedClaim

if TYPE_CHECKING:
    from .open_research import OpenResearchResult


@dataclass(frozen=True)
class FactorExplanation:
    factor: str
    contribution: str
    claim_ids: tuple[str, ...]
    source_count: int
    origin_count: int
    confidence: str
    domain: str
    origin_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompetingExplanation:
    name: str
    factor_ids: tuple[str, ...]
    distinguishing_evidence: tuple[str, ...]


@dataclass(frozen=True)
class ResearchSynthesis:
    question: str
    status: str
    thesis: str
    factors: tuple[FactorExplanation, ...]
    complementary_domains: tuple[str, ...]
    competing_explanations: tuple[CompetingExplanation, ...]
    distinguishing_evidence: tuple[str, ...]
    caveats: tuple[str, ...]
    next_actions: tuple[str, ...]

    def render(self) -> str:
        lines = [self.thesis, "", "Contributing factors:"]
        for factor in self.factors:
            lines.append(f"- [{factor.domain}] {factor.factor}: {factor.contribution}")
        if self.complementary_domains:
            lines.append("\nComplementary domains:")
            lines.append("- " + ", ".join(self.complementary_domains))
        if self.competing_explanations:
            lines.append("\nCompeting explanations (only where evidence indicates genuine alternatives):")
            for explanation in self.competing_explanations:
                lines.append(f"- {explanation.name}: " + "; ".join(explanation.distinguishing_evidence))
        if self.distinguishing_evidence:
            lines.append("\nEvidence needed to discriminate remaining alternatives:")
            lines.extend(f"- {item}" for item in self.distinguishing_evidence)
        if self.caveats:
            lines.append("\nCaveats:")
            lines.extend(f"- {item}" for item in self.caveats)
        if self.next_actions:
            lines.append("\nNext actions:")
            lines.extend(f"- {item}" for item in self.next_actions)
        return "\n".join(lines)


class ResearchSynthesisEngine:
    """Construct a cautious, multi-factor explanation from extracted claims."""

    _CAUSE_PATTERNS = (
        re.compile(r"(?P<factor>.+?)\s+(?:contributed to|led to|resulted in|caused|undermined|weakened|destabilized)\s+(?P<outcome>.+)", re.I),
        re.compile(r"(?P<factor>.+?)\s+(?:did not|does not|do not)\s+(?:contribute to|lead to|result in|cause|undermine|weaken|destabilize)\s+(?P<outcome>.+)", re.I),
        re.compile(r"(?P<outcome>.+?)\s+(?:was|were|became)\s+(?:weakened|undermined|destabilized)\s+by\s+(?P<factor>.+)", re.I),
        re.compile(r"(?P<outcome>.+?)\s+(?:because of|due to|because)\s+(?P<factor>.+)", re.I),
    )
    _NEGATION = re.compile(r"\b(?:not|never|no|neither|without|contradicts|contradicted|inconsistent)\b", re.I)
    _OUTCOME_TERMS = ("decline", "declined", "fall", "fell", "collapse", "collapsed", "end", "ended", "crisis", "weakened", "threatened")
    _PRONOUN_FACTORS = re.compile(r"^(?:this|that|it|he|she|they|these|those)\b", re.I)
    _HISTORIOGRAPHY = re.compile(r"\b(?:historians?|gibbon|theory|theories|historiography|speculat|account of the event)\b", re.I)
    _DOMAIN_TERMS = {
        "military": ("army", "armed", "military", "soldier", "frontier", "force", "war", "invasion", "goth", "goths"),
        "political": ("political", "instability", "emperor", "succession", "civil", "governance", "administr", "central rule"),
        "economic": ("economic", "economy", "tax", "fiscal", "trade", "currency", "revenue", "agriculture", "grain"),
        "demographic": ("population", "demographic", "migration", "disease", "birth"),
        "environmental": ("climate", "drought", "famine", "environment", "volcan", "temperature"),
        "religious": ("christian", "christianity", "pagan", "religion", "church"),
        "external": ("goth", "vandals", "huns", "barbar", "invasion", "external", "migrat", "frontier pressure"),
        "systemic": ("internal", "external", "institution", "imperial system", "combination of factors"),
    }

    def synthesize(self, result: "OpenResearchResult", *, max_factors: int = 8) -> ResearchSynthesis:
        candidates = self._causal_claims(result.claims)
        factors = self._factorize(candidates, result, max_factors=max_factors)
        domains = tuple(dict.fromkeys(factor.domain for factor in factors))
        competing = self._competing(factors, candidates)
        distinguishing = self._distinguishing(factors, competing)
        caveats = list(result.unresolved)
        caveats.append(
            f"{result.genealogy.finding_count} findings came from {result.genealogy.observed_origin_count} observed origins; "
            "finding count is not independent-source count."
        )
        if any(claim.confidence == "uncertain" for claim in result.claims):
            caveats.append("Some extracted claims are explicitly uncertain or attributed and remain candidate evidence.")
        status = "candidate_multi_factor_synthesis" if factors else "insufficient_explanatory_structure"
        if result.genealogy.effective_independent_count < 2:
            status = "thin_evidence_multi_factor_synthesis"
        return ResearchSynthesis(
            question=result.question,
            status=status,
            thesis=self._thesis(result.question, factors, domains),
            factors=tuple(factors),
            complementary_domains=domains,
            competing_explanations=tuple(competing),
            distinguishing_evidence=tuple(distinguishing),
            caveats=tuple(dict.fromkeys(caveats)),
            next_actions=tuple(self._next_actions(factors, competing, result)),
        )

    def _causal_claims(self, claims: Sequence[ExtractedClaim]) -> tuple[ExtractedClaim, ...]:
        return tuple(claim for claim in claims if any(pattern.search(claim.proposition) for pattern in self._CAUSE_PATTERNS))

    def _factorize(self, claims: Sequence[ExtractedClaim], result: "OpenResearchResult", *, max_factors: int) -> list[FactorExplanation]:
        buckets: dict[str, list[ExtractedClaim]] = {}
        for claim in claims:
            factor = self._factor_text(claim.proposition)
            if factor:
                buckets.setdefault(_normalize(factor), []).append(claim)
        ranked = sorted(buckets.values(), key=lambda members: -len(members))[:max_factors]
        origin_by_claim = {claim_id: origin.root_id for origin in result.genealogy.origins for claim_id in origin.claim_ids}
        factors: list[FactorExplanation] = []
        for members in ranked:
            source_ids = {claim.source for claim in members}
            origin_ids = {origin_by_claim.get(claim.id) for claim in members} - {None}
            factor_text = self._factor_text(members[0].proposition)
            factors.append(FactorExplanation(
                factor=factor_text,
                contribution="; ".join(dict.fromkeys(claim.proposition for claim in members))[:700],
                claim_ids=tuple(claim.id for claim in members),
                source_count=len(source_ids),
                origin_count=len(origin_ids),
                confidence="candidate_uncertain" if any(claim.confidence == "uncertain" for claim in members) else "candidate",
                domain=self._domain(factor_text),
                origin_ids=tuple(sorted(origin_ids)),
            ))
        return factors

    def _factor_text(self, text: str) -> str:
        if self._HISTORIOGRAPHY.search(text):
            return ""
        lowered = text.lower()
        for pattern in self._CAUSE_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            factor = _trim_factor(match.group("factor"))
            if not any(term in lowered for term in self._OUTCOME_TERMS):
                continue
            if self._PRONOUN_FACTORS.search(factor) or len(factor.split()) < 2:
                continue
            if self._domain(factor) == "other":
                continue
            return factor
        return ""

    def _domain(self, text: str) -> str:
        lowered = text.lower()
        scores = {domain: sum(lowered.count(term) for term in terms) for domain, terms in self._DOMAIN_TERMS.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] else "other"

    def _competing(self, factors: Sequence[FactorExplanation], claims: Sequence[ExtractedClaim]) -> list[CompetingExplanation]:
        contrary = [claim for claim in claims if self._NEGATION.search(claim.proposition)]
        if not contrary:
            return []
        result: list[CompetingExplanation] = []
        for claim in contrary[:4]:
            factor = self._factor_text(claim.proposition)
            if not factor:
                continue
            result.append(CompetingExplanation(
                name=f"alternative involving {factor}",
                factor_ids=(factor,),
                distinguishing_evidence=(
                    "Test the contrary proposition against the positive contribution claims using independent evidence and the same outcome/time window.",
                ),
            ))
        return result

    def _distinguishing(self, factors: Sequence[FactorExplanation], competing: Sequence[CompetingExplanation]) -> list[str]:
        if competing:
            return [
                "Compare the competing propositions with independent evidence that measures mechanism, timing, and outcome together.",
                "Check whether the apparently competing factors can instead operate jointly; do not force mutual exclusivity without evidence.",
            ]
        if len(factors) < 2:
            return ["Acquire independent evidence that directly connects the leading factor to the outcome over the relevant period."] if factors else []
        first, second = factors[0], factors[1]
        return [
            f"Test whether {first.factor} contributes independently to the outcome alongside {second.factor}.",
            f"Search for evidence of a mechanism linking {first.factor} to {second.factor}, rather than assuming interaction.",
        ]

    def _thesis(self, question: str, factors: Sequence[FactorExplanation], domains: Sequence[str]) -> str:
        if not factors:
            return f"Cognitia cannot yet construct a grounded multi-factor explanation for: {question}"
        domain_text = ", ".join(domains)
        return (
            f"The current candidate evidence does not justify reducing {question} to one cause. "
            f"It identifies multiple potentially complementary contributing factors across {domain_text}. "
            "The synthesis describes observed candidate contribution mechanisms without promoting extraction alone to established knowledge."
        )

    def _next_actions(self, factors: Sequence[FactorExplanation], competing: Sequence[CompetingExplanation], result: "OpenResearchResult") -> list[str]:
        actions = [
            "Acquire independent evidence for each leading factor and preserve source genealogy.",
            "Separate temporal association from causal contribution by requiring evidence of mechanism as well as timing.",
        ]
        if competing:
            actions.append("Run a discriminating investigation against the explicitly contrary propositions.")
        elif len(factors) >= 2:
            actions.append("Investigate whether leading factors interact or form causal chains; record only links supported by evidence.")
        if result.genealogy.effective_independent_count < 2:
            actions.append("Increase independent source-origin diversity before promoting the synthesis to durable knowledge.")
        return actions


def _normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _trim_factor(value: str) -> str:
    value = re.sub(r"^(according to|some historians|most historians|the traditional view)\s+", "", value, flags=re.I)
    return value.strip(" ,;:.")[:220]
