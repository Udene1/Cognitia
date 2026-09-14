"""Complete, serializable inspection traces for Cognitia research episodes.

A trace is the boundary between Cognitia's internal structured cognition and
an external researcher. It preserves the path from question to search choice,
acquisition, claims, hypotheses, synthesis, answer, epistemic state, and later
revision. It is intentionally data-first so a UI can render it without
re-running cognition or scraping log text.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .answering import AnswerRevision, CandidateAnswer
from .open_research import OpenResearchResult
from .research_synthesis import ResearchSynthesis


@dataclass(frozen=True)
class ResearchTrace:
    question: str
    research_status: str
    stop_reason: str
    search_plan: tuple[dict[str, Any], ...]
    evidence_acquired: tuple[dict[str, Any], ...]
    claims_formed: tuple[dict[str, Any], ...]
    hypotheses_considered: tuple[dict[str, Any], ...]
    synthesis: dict[str, Any]
    final_answer: dict[str, Any]
    confidence: str
    uncertainty: tuple[str, ...]
    revision: dict[str, Any] | None = None

    @classmethod
    def build(
        cls,
        result: OpenResearchResult,
        synthesis: ResearchSynthesis,
        answer: CandidateAnswer,
        *,
        revision: AnswerRevision | None = None,
    ) -> "ResearchTrace":
        searches: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        claims: list[dict[str, Any]] = []
        for index, research_round in enumerate(result.rounds, start=1):
            action = research_round.action
            searches.append({
                "round": index,
                "query": action.query.objective,
                "terms": list(action.query.terms),
                "purpose": action.purpose,
                "priority": action.priority,
                "parent": action.parent,
                "expected_information_gain": research_round.expected_information_gain,
                "decision_rationale": research_round.decision_rationale,
                "search_observations": [
                    {
                        "id": obs.id,
                        "source": obs.source,
                        "content": obs.content,
                        "reliability": obs.reliability,
                        "metadata": dict(obs.metadata),
                    }
                    for obs in research_round.search_observations
                ],
            })
            for document in research_round.documents:
                metadata = dict(document.metadata)
                evidence.append({
                    "id": document.id,
                    "source": document.source,
                    "reliability": document.reliability,
                    "url": metadata.get("url"),
                    "query": metadata.get("query"),
                    "search_observation": metadata.get("search_observation"),
                    "content": document.content,
                    "round": index,
                })
            for claim in research_round.claims:
                claims.append({
                    "id": claim.id,
                    "proposition": claim.proposition,
                    "observation_id": claim.observation_id,
                    "source": claim.source,
                    "sentence": claim.sentence,
                    "confidence": claim.confidence,
                    "temporal_markers": list(claim.temporal_markers),
                    "entities": list(claim.entities),
                    "relations": list(claim.relations),
                    "uncertainty_markers": list(claim.uncertainty_markers),
                    "polarity": claim.polarity,
                    "attribution_markers": list(claim.attribution_markers),
                    "round": index,
                })

        claim_ids = {claim["id"] for claim in claims}
        hypotheses: list[dict[str, Any]] = []
        for factor in synthesis.factors:
            hypotheses.append({
                "id": "hypothesis:" + factor.factor,
                "kind": "candidate_factor",
                "name": factor.factor,
                "domain": factor.domain,
                "claim_ids": [claim_id for claim_id in factor.claim_ids if claim_id in claim_ids],
                "source_count": factor.source_count,
                "origin_count": factor.origin_count,
                "confidence": factor.confidence,
                "contribution": factor.contribution,
            })
        for competing in synthesis.competing_explanations:
            hypotheses.append({
                "id": "alternative:" + competing.name,
                "kind": "competing_explanation",
                "name": competing.name,
                "factor_ids": list(competing.factor_ids),
                "distinguishing_evidence": list(competing.distinguishing_evidence),
            })

        synthesis_payload = asdict(synthesis)
        synthesis_payload["factors"] = [asdict(factor) for factor in synthesis.factors]
        synthesis_payload["competing_explanations"] = [asdict(item) for item in synthesis.competing_explanations]
        answer_payload = asdict(answer)
        return cls(
            question=result.question,
            research_status=result.status,
            stop_reason=result.stop_reason,
            search_plan=tuple(searches),
            evidence_acquired=tuple(evidence),
            claims_formed=tuple(claims),
            hypotheses_considered=tuple(hypotheses),
            synthesis=synthesis_payload,
            final_answer=answer_payload,
            confidence=answer.epistemic.confidence,
            uncertainty=answer.uncertainty,
            revision=asdict(revision) if revision else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
