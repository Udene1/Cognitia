"""Evidence-derived adaptive research over the open-research pipeline.

The first round is selected normally. Each later action is constructed only
from the immediately preceding evidence state: conflicts, claim identity
confidence, and acquired claims. This deliberately tests trajectory causality
without introducing an LLM or a question-specific search script.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .document_claims import DocumentClaimExtractor, ExtractedClaim
from .environment import EnvironmentObservation
from .evidence.claim_identity import ClaimIdentityMatcher
from .evidence.genealogy import EvidenceGenealogyBuilder
from .language import AnswerContract, analyze_question
from .open_research import (
    ClaimCluster,
    OpenResearchResult,
    OpenResearchRound,
    _cluster_claims,
    _stop_reason,
    _unresolved_questions,
)
from .research_search import ResearchSearchPlanner, SearchAction
from .web_research import LiveWebResearchSession


@dataclass(frozen=True)
class ResearchInformationNeed:
    """The explicit gap that caused the next research action."""

    kind: str
    description: str
    source_claim_ids: tuple[str, ...]
    source_document_ids: tuple[str, ...]


@dataclass(frozen=True)
class AdaptiveResearchEpisode:
    """A bounded research episode whose later actions depend on prior evidence."""

    result: OpenResearchResult
    information_needs: tuple[ResearchInformationNeed, ...]


class AdaptiveOpenResearch:
    """Run bounded research where each new action is derived from prior evidence."""

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

    def investigate(self, question: str, *, max_rounds: int = 2,
                    search_results: int = 5, documents_per_round: int = 3,
                    claims_per_document: int = 20) -> AdaptiveResearchEpisode:
        if not question.strip():
            raise ValueError("question is required")
        if max_rounds < 1:
            raise ValueError("max_rounds must be positive")

        answer_contract = analyze_question(question).contract
        first = self.planner.plan(question, max_actions=1).actions[0]
        rounds: list[OpenResearchRound] = []
        information_needs: list[ResearchInformationNeed] = []
        all_claims: list[ExtractedClaim] = []
        all_documents: list[EnvironmentObservation] = []
        seen_documents: set[str] = set()
        action = first

        for sequence in range(max_rounds):
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

            need = None
            if sequence > 0:
                need = information_needs[-1]

            rounds.append(OpenResearchRound(
                action=action,
                search_observations=bundle.search_observations,
                documents=documents,
                claims=claims,
                clusters=clusters,
                decision_rationale=_decision_rationale(action, need),
                expected_information_gain=round(action.priority, 3),
                information_need=need.description if need else None,
                information_need_source_claim_ids=need.source_claim_ids if need else (),
                information_need_source_document_ids=need.source_document_ids if need else (),
                parent_action_id=rounds[-1].action_id if rounds else None,
            ))

            if sequence + 1 >= max_rounds:
                break
            next_action, next_need = self._derive_next_action(question, rounds[-1], rounds)
            if next_action is None or next_need is None:
                break
            information_needs.append(next_need)
            action = next_action

        clusters = _cluster_claims(all_claims, self.identity)
        genealogy = self.genealogy.assess(all_documents, all_claims)
        unresolved = _unresolved_questions(question, rounds, clusters, genealogy)
        result = OpenResearchResult(
            question=question,
            rounds=tuple(rounds),
            claims=tuple(all_claims),
            clusters=clusters,
            unresolved=tuple(unresolved),
            genealogy=genealogy,
            stop_reason=_stop_reason(rounds, genealogy),
            answer_contract=answer_contract,
        )
        return AdaptiveResearchEpisode(result, tuple(information_needs))

    def _derive_next_action(
        self,
        question: str,
        previous: OpenResearchRound,
        rounds: Sequence[OpenResearchRound],
    ) -> tuple[SearchAction | None, ResearchInformationNeed | None]:
        conflicting = tuple(cluster for cluster in previous.clusters if cluster.conflict)
        if conflicting:
            claims = tuple(cluster.representative for cluster in conflicting)
            objective = "Resolve conflicting evidence: " + " | ".join(claim.proposition for claim in claims[:2])
            need = ResearchInformationNeed(
                "conflict_resolution",
                objective,
                tuple(claim.id for claim in claims),
                tuple(document.id for document in previous.documents),
            )
        elif previous.clusters:
            target = min(previous.clusters, key=lambda cluster: cluster.identity_confidence)
            claim = target.representative
            objective = f"Find independent evidence for: {claim.proposition}"
            need = ResearchInformationNeed(
                "independent_evidence",
                objective,
                (claim.id,),
                tuple(document.id for document in previous.documents),
            )
        elif previous.claims:
            claim = previous.claims[0]
            objective = f"Find primary evidence for: {claim.proposition}"
            need = ResearchInformationNeed(
                "claim_verification",
                objective,
                (claim.id,),
                tuple(document.id for document in previous.documents),
            )
        else:
            objective = f"Find evidence relevant to: {question}"
            need = ResearchInformationNeed(
                "evidence_acquisition",
                objective,
                (),
                tuple(document.id for document in previous.documents),
            )

        planned = self.planner.plan(objective, max_actions=1)
        if not planned.actions:
            return None, None
        candidate = planned.actions[0]
        action = SearchAction(
            candidate.query,
            candidate.purpose,
            candidate.priority,
            parent=_action_id(previous),
        )
        return action, need


def _action_id(research_round: OpenResearchRound) -> str:
    return f"{research_round.action.purpose}:{research_round.action.query.objective.strip().lower()}"


def _decision_rationale(action: SearchAction, need: ResearchInformationNeed | None) -> str:
    if need is None:
        return f"initial action selected by planner (priority={action.priority:.2f})"
    evidence = ", ".join(need.source_claim_ids) or "no claim identity"
    return (
        f"selected from preceding evidence need={need.kind}; "
        f"source_claims={evidence}; parent={action.parent}; priority={action.priority:.2f}"
    )
