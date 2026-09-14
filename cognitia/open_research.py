"""Open-ended research orchestration with evidence-origin accounting.

The research system deliberately stops short of pretending extracted claims are
truth. It distinguishes repeated findings from repeated propositions, tracks
source genealogy, and now crosses an explicit durable-knowledge boundary:
validated research conclusions may be promoted, and later investigations can
read those durable propositions before choosing fresh searches.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Sequence

from .document_claims import DocumentClaimExtractor, ExtractedClaim
from .environment import EnvironmentObservation
from .evidence.claim_identity import ClaimIdentityMatcher
from .evidence.genealogy import EvidenceGenealogyBuilder, GenealogyAssessment
from .knowledge.model import KnowledgeItem, KnowledgeSource
from .knowledge.validated import KnowledgeTest, ValidatedKnowledgeStore
from .language import AnswerContract, analyze_question
from .research_search import ResearchSearchPlanner, SearchAction
from .research_synthesis import ResearchSynthesis, ResearchSynthesisEngine
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
    answer_contract: AnswerContract | None = None
    prior_knowledge: tuple[KnowledgeItem, ...] = ()
    promoted_knowledge: tuple[KnowledgeItem, ...] = ()

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
    """Run bounded, real-web research with durable knowledge feedback."""

    def __init__(self, *, web: LiveWebResearchSession | None = None,
                 planner: ResearchSearchPlanner | None = None,
                 extractor: DocumentClaimExtractor | None = None,
                 genealogy: EvidenceGenealogyBuilder | None = None,
                 identity: ClaimIdentityMatcher | None = None,
                 knowledge_store: ValidatedKnowledgeStore | None = None) -> None:
        self.web = web or LiveWebResearchSession()
        self.planner = planner or ResearchSearchPlanner()
        self.extractor = extractor or DocumentClaimExtractor()
        self.genealogy = genealogy or EvidenceGenealogyBuilder()
        self.identity = identity or ClaimIdentityMatcher()
        self.knowledge_store = knowledge_store

    def investigate(self, question: str, *, max_rounds: int = 4,
                    search_results: int = 5, documents_per_round: int = 3,
                    claims_per_document: int = 20) -> OpenResearchResult:
        if not question.strip():
            raise ValueError("question is required")
        answer_contract = analyze_question(question).contract
        prior_knowledge = self._relevant_knowledge(question)
        plan = self.planner.plan(question, max_actions=max_rounds)
        if prior_knowledge:
            plan = self._apply_knowledge_prior(plan, prior_knowledge)
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
                    decision_rationale=(
                        f"selected for {action.purpose} (priority={action.priority:.2f})"
                        + ("; informed by durable knowledge" if prior_knowledge else "")
                    ),
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
            answer_contract=answer_contract,
            prior_knowledge=prior_knowledge,
        )

    def investigate_and_synthesize(self, question: str, *, max_rounds: int = 4,
                                   search_results: int = 5, documents_per_round: int = 3,
                                   claims_per_document: int = 20) -> tuple[OpenResearchResult, ResearchSynthesis]:
        """Research, synthesize, and promote only independently corroborated conclusions."""
        result = self.investigate(
            question,
            max_rounds=max_rounds,
            search_results=search_results,
            documents_per_round=documents_per_round,
            claims_per_document=claims_per_document,
        )
        synthesis = ResearchSynthesisEngine().synthesize(result)
        promoted = self._promote_synthesis(synthesis, result)
        if promoted:
            result = OpenResearchResult(
                question=result.question,
                rounds=result.rounds,
                claims=result.claims,
                clusters=result.clusters,
                unresolved=result.unresolved,
                genealogy=result.genealogy,
                stop_reason=result.stop_reason,
                answer_contract=result.answer_contract,
                prior_knowledge=result.prior_knowledge,
                promoted_knowledge=promoted,
            )
        return result, synthesis

    def _relevant_knowledge(self, question: str) -> tuple[KnowledgeItem, ...]:
        if self.knowledge_store is None:
            return ()
        tokens = _tokens(question)
        scored: list[tuple[float, KnowledgeItem]] = []
        for item in self.knowledge_store.items():
            text = f"{item.subject} {item.predicate} {item.value} {item.scope}"
            item_tokens = _tokens(text)
            overlap = len(tokens & item_tokens) / max(1, len(tokens | item_tokens))
            if overlap >= 0.08:
                scored.append((overlap * item.source.reliability, item))
        scored.sort(key=lambda pair: (-pair[0], pair[1].id))
        return tuple(item for _, item in scored[:6])

    @staticmethod
    def _apply_knowledge_prior(plan, prior_knowledge: Sequence[KnowledgeItem]):
        from dataclasses import replace
        hints = tuple(_memory_terms(item.value) for item in prior_knowledge)
        flat_hints = tuple(dict.fromkeys(term for group in hints for term in group))[:8]
        if not flat_hints:
            return plan
        actions = []
        for action in plan.actions:
            objective = f"{action.query.objective} {' '.join(flat_hints)}"
            actions.append(replace(action, query=replace(action.query, objective=objective)))
        return replace(plan, actions=tuple(actions))

    def _promote_synthesis(self, synthesis: ResearchSynthesis, result: OpenResearchResult) -> tuple[KnowledgeItem, ...]:
        if self.knowledge_store is None:
            return ()
        # A synthesis-level conclusion is promotable only when the research
        # episode itself has at least two independent source origins. Individual
        # factors remain candidates unless that specific factor has multi-origin
        # support, so this does not turn extraction into causal truth.
        if result.genealogy.effective_independent_count < 2 or not synthesis.factors:
            return ()
        digest = hashlib.sha256(synthesis.question.encode()).hexdigest()[:20]
        item = KnowledgeItem(
            subject=synthesis.question,
            predicate="research_conclusion",
            value=synthesis.thesis,
            source=KnowledgeSource("live_research", f"research:{digest}", reliability=0.85),
            id=f"knowledge:research:{digest}",
            scope="research-corroborated",
        )
        origin_ids = tuple(origin.root_id for origin in result.genealogy.origins)[: result.genealogy.effective_independent_count]
        tests = tuple(
            KnowledgeTest(
                id=f"research-origin:{digest}:{origin}",
                knowledge_id=item.id,
                passed=True,
                reliability=0.85,
            )
            for origin in origin_ids
        )
        try:
            self.knowledge_store.promote(item, tests)
        except ValueError:
            return ()
        return (item,)


def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", str(value).lower()) if len(token) > 2}


def _memory_terms(value: object) -> tuple[str, ...]:
    return tuple(token for token in re.findall(r"[a-z0-9]+", str(value).lower()) if len(token) > 3)[:6]


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
    if genealogy.finding_count > genealogy.observed_origin_count:
        gaps.append("Multiple findings may share source origins; finding count must not be treated as independent evidence count.")
    if genealogy.effective_independent_count < 2:
        gaps.append("Independent source-origin diversity remains too thin for durable promotion.")
    return gaps


def _stop_reason(rounds: Sequence[OpenResearchRound], genealogy: GenealogyAssessment) -> str:
    if genealogy.effective_independent_count < 2:
        return "independent_evidence_budget_exhausted"
    if rounds:
        return "bounded_search_budget_exhausted"
    return "no_research_round"
