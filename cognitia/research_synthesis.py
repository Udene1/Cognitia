"""Grounded synthesis for multi-factor research questions.

This layer turns a candidate evidence landscape into a structured explanatory
answer. It never upgrades extracted claims to truth: every factor remains a
candidate explanation with explicit source/origin accounting and uncertainty.
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
    competing_explanations: tuple[CompetingExplanation, ...]
    distinguishing_evidence: tuple[str, ...]
    caveats: tuple[str, ...]
    next_actions: tuple[str, ...]

    def render(self) -> str:
        lines = [self.thesis, "", "Contributing factors:"]
        for factor in self.factors:
            lines.append(f"- {factor.factor}: {factor.contribution}")
        if self.competing_explanations:
            lines.append("\nCompeting explanations:")
            for explanation in self.competing_explanations:
                lines.append(f"- {explanation.name}: " + "; ".join(explanation.distinguishing_evidence))
        if self.distinguishing_evidence:
            lines.append("\nEvidence that would distinguish them:")
            lines.extend(f"- {item}" for item in self.distinguishing_evidence)
        if self.caveats:
            lines.append("\nCaveats:")
            lines.extend(f"- {item}" for item in self.caveats)
        if self.next_actions:
            lines.append("\nNext actions:")
            lines.extend(f"- {item}" for item in self.next_actions)
        return "\n".join(lines)


class ResearchSynthesisEngine:
    """Construct a cautious explanatory synthesis from extracted claims."""

    _CAUSE_PATTERNS = (
        re.compile(r"(?P<factor>.+?)\s+(?:contributed to|led to|resulted in|caused|undermined|weakened|destabilized)\s+(?P<outcome>.+)", re.I),
        re.compile(r"(?P<outcome>.+?)\s+(?:was|were|became)\s+(?:weakened|undermined|destabilized)\s+by\s+(?P<factor>.+)", re.I),
        re.compile(r"(?P<outcome>.+?)\s+(?:because of|due to|because)\s+(?P<factor>.+)", re.I),
    )
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
        domains = self._domains(factors)
        competing = self._competing(domains)
        distinguishing = self._distinguishing(factors)
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
            thesis=self._thesis(result.question, factors),
            factors=tuple(factors),
            competing_explanations=tuple(competing),
            distinguishing_evidence=tuple(distinguishing),
            caveats=tuple(dict.fromkeys(caveats)),
            next_actions=tuple(self._next_actions(factors, result)),
        )

    def _causal_claims(self, claims: Sequence[ExtractedClaim]) -> tuple[ExtractedClaim, ...]:
        return tuple(claim for claim in claims if any(pattern.search(claim.proposition) for pattern in self._CAUSE_PATTERNS))

    def _factorize(self, claims: Sequence[ExtractedClaim], result: "OpenResearchResult", *, max_factors: int) -> list[FactorExplanation]:
        buckets: dict[str, list[ExtractedClaim]] = {}
        for claim in claims:
            factor = self._factor_text(claim.proposition)
            if factor:
                buckets.setdefault(_normalize(factor), []).append(claim)
        ranked = sorted(buckets.values(), key=lambda members: (-len(members), members[0].id))[:max_factors]
        origin_by_claim = {claim_id: origin.root_id for origin in result.genealogy.origins for claim_id in origin.claim_ids}
        factors: list[FactorExplanation] = []
        for members in ranked:
            source_ids = {claim.source for claim in members}
            origin_ids = {origin_by_claim.get(claim.id) for claim in members} - {None}
            factors.append(FactorExplanation(
                factor=self._factor_text(members[0].proposition),
                contribution="; ".join(dict.fromkeys(claim.proposition for claim in members))[:600],
                claim_ids=tuple(claim.id for claim in members),
                source_count=len(source_ids),
                origin_count=len(origin_ids),
                confidence="candidate_uncertain" if any(claim.confidence == "uncertain" for claim in members) else "candidate",
            ))
        return factors

    def _factor_text(self, text: str) -> str:
        lowered = text.lower()
        if self._HISTORIOGRAPHY.search(text):
            return ""
        for pattern in self._CAUSE_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            factor = _trim_factor(match.group("factor"))
            outcome = match.group("outcome").lower()
            if not any(term in lowered for term in self._OUTCOME_TERMS):
                continue
            if not any(term in outcome for term in self._OUTCOME_TERMS):
                continue
            if self._PRONOUN_FACTORS.search(factor):
                continue
            if len(factor.split()) < 2:
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

    def _domains(self, factors: Sequence[FactorExplanation]) -> dict[str, list[FactorExplanation]]:
        result: dict[str, list[FactorExplanation]] = {}
        for factor in factors:
            result.setdefault(self._domain(factor.factor), []).append(factor)
        return result

    def _competing(self, domains: dict[str, list[FactorExplanation]]) -> list[CompetingExplanation]:
        groups = [(name, members) for name, members in domains.items() if members]
        if len(groups) < 2:
            return []
        result: list[CompetingExplanation] = []
        for name, members in groups[:4]:
            alternatives = [other for other, _ in groups if other != name]
            result.append(CompetingExplanation(
                name=f"{name}-weighted explanation",
                factor_ids=tuple(factor.factor for factor in members),
                distinguishing_evidence=tuple(
                    f"Compare {name} evidence against {other} evidence under the same historical period and outcome definition."
                    for other in alternatives[:2]
                ),
            ))
        return result

    def _distinguishing(self, factors: Sequence[FactorExplanation]) -> list[str]:
        domains = list(dict.fromkeys(self._domain(factor.factor) for factor in factors))
        if len(domains) < 2:
            return ["Acquire independent evidence that directly measures the leading factor and the claimed outcome over the same period."] if factors else []
        return [
            f"Find evidence that separates {domains[index]} effects from {domains[index + 1]} effects rather than merely reporting both."
            for index in range(min(len(domains) - 1, 4))
        ]

    def _thesis(self, question: str, factors: Sequence[FactorExplanation]) -> str:
        if not factors:
            return f"Cognitia cannot yet construct a grounded multi-factor explanation for: {question}"
        names = ", ".join(dict.fromkeys(self._domain(factor.factor) for factor in factors))
        return (
            f"The current candidate evidence does not reduce {question} to one cause. "
            f"It points to a multi-factor explanation involving {names}. "
            "The factors below describe candidate contribution mechanisms; they are not promoted to established knowledge by extraction alone."
        )

    def _next_actions(self, factors: Sequence[FactorExplanation], result: "OpenResearchResult") -> list[str]:
        actions = [
            "Acquire independent evidence for the strongest competing factor domains.",
            "Separate correlation from causal contribution by searching for evidence tied to timing and mechanism.",
        ]
        if len(factors) >= 2:
            actions.append("Run a discriminating investigation designed to distinguish at least two leading factor combinations.")
        if result.genealogy.effective_independent_count < 2:
            actions.append("Increase independent source-origin diversity before promoting the synthesis.")
        return actions


def _normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _trim_factor(value: str) -> str:
    value = re.sub(r"^(according to|some historians|most historians|the traditional view)\s+", "", value, flags=re.I)
    return value.strip(" ,;:.")[:220]
