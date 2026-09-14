"""Open-ended research orchestration with evidence-origin accounting.

The research system deliberately stops short of pretending extracted claims are
truth. It also distinguishes repeated findings from repeated propositions and
tracks source genealogy before evidence is allowed to influence conclusions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .document_claims import DocumentClaimExtractor, ExtractedClaim
from .environment import EnvironmentObservation
from .evidence.claim_identity import ClaimIdentityMatcher
from .evidence.genealogy import EvidenceGenealogyBuilder, GenealogyAssessment
from .research_search import ResearchSearchPlanner, SearchAction
from .web_research import LiveWebResearchSession


@dataclass(frozen=True)
class ClaimCluster:
    representative: ExtractedClaim
    members: tuple[ExtractedClaim, ...]
    source_ids: tuple[str, ...]
    conflict: bool
    identity_confidence: float
    identity_basis: tuple[str, ...]


@dataclass(frozen=True)
class OpenResearchRound:
    action: SearchAction
    search_observations: tuple[EnvironmentObservation, ...]
    documents: tuple[EnvironmentObservation, ...]
    claims: tuple[ExtractedClaim, ...]
    clusters: tuple[ClaimCluster, ...]
    decision_rationale: str
    expected_information_gain: float


@dataclass(frozen=True)
class OpenResearchResult:
    question: str
    rounds: tuple[OpenResearchRound, ...]
    claims: tuple[ExtractedClaim, ...]
    clusters: tuple[ClaimCluster, ...]
    unresolved: tuple[str, ...]
    genealogy: GenealogyAssessment
    stop_reason: str

    @property
    def status(self) -> str:
        if not self.claims:
            return "no_candidate_claims"
        if any(cluster.conflict for cluster in self.clusters):
            return "conflicted"
        if self.genealogy.effective_independent_count < 2:
            return "thin_independent_evidence"
        return "candidate_evidence_landscape"


class OpenEndedResearch:
    """Run bounded, real-web research while preserving evidence genealogy."""

    def __init__(self, *, web: LiveWebResearchSession | None = None,
                 planner: ResearchSearchPlanner | None = None,
                 extractor: DocumentClaimExtractor | None = None,
                 genealogy: EvidenceGenealogyBuilder | None = None,
                 identity: ClaimIdentityMatcher | None = None) -> None:
        self.web = web or LiveWebResearchSession()
        self.planner = planner or ResearchSearchPlanner()
        self.extractor = extractor or DocumentClaimExtractor()
        self.genealogy = genealogy or EvidenceGenealogyBuilder()
        self.identity = identity or ClaimIdentityMatcher()

    def investigate(self, question: str, *, max_rounds: int = 4,
                    search_results: int = 5, documents_per_round: int = 3,
                    claims_per_document: int = 20) -> OpenResearchResult:
        if not question.strip():
            raise ValueError("question is required")
        plan = self.planner.plan(question, max_actions=max_rounds)
        rounds: list[OpenResearchRound] = []
        all_claims: list[ExtractedClaim] = []
        all_documents: list[EnvironmentObservation] = []
        seen_documents: set[str] = set()

        for action in plan.actions:
            bundle = self.web.investigate(
                action.query.objective,
                limit=search_results,
                fetch_limit=documents_per_round,
            )
            documents = tuple(doc for doc in bundle.document_observations if doc.id not in seen_documents)
            seen_documents.update(doc.id for doc in documents)
            claims = self.extractor.extract_many(documents, limit_per_document=claims_per_document)
            all_claims.extend(claims)
            all_documents.extend(documents)
            clusters = _cluster_claims(claims, self.identity)
            rounds.append(
                OpenResearchRound(
                    action=action,
                    search_observations=bundle.search_observations,
                    documents=documents,
                    claims=claims,
                    clusters=clusters,
                    decision_rationale=f"selected for {action.purpose} (priority={action.priority:.2f})",
                    expected_information_gain=round(action.priority, 3),
                )
            )

        clusters = _cluster_claims(all_claims, self.identity)
        genealogy = self.genealogy.assess(all_documents, all_claims)
        unresolved = _unresolved_questions(question, rounds, clusters, genealogy)
        stop_reason = _stop_reason(rounds, genealogy)
        return OpenResearchResult(
            question=question,
            rounds=tuple(rounds),
            claims=tuple(all_claims),
            clusters=clusters,
            unresolved=tuple(unresolved),
            genealogy=genealogy,
            stop_reason=stop_reason,
        )


def _cluster_claims(claims: Sequence[ExtractedClaim], matcher: ClaimIdentityMatcher) -> tuple[ClaimCluster, ...]:
    identities = matcher.match(claims)
    by_id = {claim.id: claim for claim in claims}
    result: list[ClaimCluster] = []
    for identity in identities:
        members = tuple(by_id[claim_id] for claim_id in identity.matched_claim_ids)
        polarities = {_polarity(member.proposition) for member in members}
        polarities.discard("unknown")
        result.append(
            ClaimCluster(
                representative=members[0],
                members=members,
                source_ids=tuple(dict.fromkeys(member.source for member in members)),
                conflict=len(polarities) > 1,
                identity_confidence=identity.confidence,
                identity_basis=identity.basis,
            )
        )
    return tuple(result)


def _polarity(text: str) -> str:
    lowered = text.lower()
    return "negative" if any(token in lowered.split() for token in ("not", "no", "never", "without", "cannot", "can't", "didn't", "doesn't", "isn't", "wasn't")) else "positive"


def _unresolved_questions(question: str, rounds: Sequence[OpenResearchRound],
                          clusters: Sequence[ClaimCluster], genealogy: GenealogyAssessment) -> list[str]:
    gaps: list[str] = []
    if not rounds:
        gaps.append("No search round produced observations.")
    if not any(research_round.documents for research_round in rounds):
        gaps.append("No source documents were retrieved; search snippets are insufficient for deeper interpretation.")
    if not clusters:
        gaps.append("No candidate claims were extracted from acquired documents.")
    if any(cluster.conflict for cluster in clusters):
        gaps.append("At least one claim identity group contains lexical polarity conflict; independent verification is required.")
    if genealogy.finding_count > genealogy.observed_origin_count:
        gaps.append(
            f"{genealogy.finding_count} findings came from {genealogy.observed_origin_count} observed origins; "
            "finding count must not be interpreted as independent-source count."
        )
    if genealogy.effective_independent_count < 2:
        gaps.append("Fewer than two candidate independent origins are available; corroboration remains weak.")
    gaps.append(f"The current result is an evidence landscape for: {question}")
    return gaps


def _stop_reason(rounds: Sequence[OpenResearchRound], genealogy: GenealogyAssessment) -> str:
    if not rounds:
        return "no_search_rounds"
    if genealogy.effective_independent_count < 2:
        return "independent_evidence_budget_exhausted"
    return "bounded_search_budget_exhausted"
