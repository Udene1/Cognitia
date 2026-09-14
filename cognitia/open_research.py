"""Open-ended research experiment orchestration.

The experiment deliberately asks Cognitia to produce a structured evidence
landscape rather than a fabricated natural-language answer. Search, document
acquisition, claim extraction, and contradiction signals remain inspectable.
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from typing import Sequence

from .adaptive_web_research import AdaptiveWebResearch
from .document_claims import DocumentClaimExtractor, ExtractedClaim
from .environment import EnvironmentObservation
from .research_search import ResearchSearchPlanner, SearchAction
from .web_research import LiveWebResearchSession, WebResearchBundle


@dataclass(frozen=True)
class ClaimCluster:
    representative: ExtractedClaim
    members: tuple[ExtractedClaim, ...]
    source_ids: tuple[str, ...]
    conflict: bool


@dataclass(frozen=True)
class OpenResearchRound:
    action: SearchAction
    search_observations: tuple[EnvironmentObservation, ...]
    documents: tuple[EnvironmentObservation, ...]
    claims: tuple[ExtractedClaim, ...]
    clusters: tuple[ClaimCluster, ...]


@dataclass(frozen=True)
class OpenResearchResult:
    question: str
    rounds: tuple[OpenResearchRound, ...]
    claims: tuple[ExtractedClaim, ...]
    clusters: tuple[ClaimCluster, ...]
    unresolved: tuple[str, ...]

    @property
    def status(self) -> str:
        if not self.claims:
            return "no_candidate_claims"
        if any(cluster.conflict for cluster in self.clusters):
            return "conflicted"
        if len(self.claims) < 2:
            return "thin_evidence"
        return "candidate_evidence_landscape"


class OpenEndedResearch:
    """Run a bounded, real-web experiment on an unseen question."""

    def __init__(self, *, web: LiveWebResearchSession | None = None,
                 planner: ResearchSearchPlanner | None = None,
                 extractor: DocumentClaimExtractor | None = None) -> None:
        self.web = web or LiveWebResearchSession()
        self.planner = planner or ResearchSearchPlanner()
        self.extractor = extractor or DocumentClaimExtractor()

    def investigate(self, question: str, *, max_rounds: int = 4,
                    search_results: int = 5, documents_per_round: int = 3,
                    claims_per_document: int = 20) -> OpenResearchResult:
        if not question.strip():
            raise ValueError("question is required")
        plan = self.planner.plan(question, max_actions=max_rounds)
        rounds: list[OpenResearchRound] = []
        all_claims: list[ExtractedClaim] = []
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
            clusters = _cluster_claims(claims)
            rounds.append(OpenResearchRound(action, bundle.search_observations, documents, claims, clusters))

        clusters = _cluster_claims(all_claims)
        unresolved = _unresolved_questions(question, rounds, clusters)
        return OpenResearchResult(question, tuple(rounds), tuple(all_claims), clusters, tuple(unresolved))


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(?:is|are|was|were|the|a|an|of|to|in|on|for|and)\b", " ", text)
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _cluster_claims(claims: Sequence[ExtractedClaim]) -> tuple[ClaimCluster, ...]:
    clusters: list[list[ExtractedClaim]] = []
    for claim in claims:
        key = _normalize(claim.proposition)
        placed = False
        for cluster in clusters:
            similarity = SequenceMatcher(None, key, _normalize(cluster[0].proposition)).ratio()
            if similarity >= 0.72:
                cluster.append(claim)
                placed = True
                break
        if not placed:
            clusters.append([claim])

    result: list[ClaimCluster] = []
    for members in clusters:
        polarities = {_polarity(member.proposition) for member in members}
        polarities.discard("unknown")
        conflict = len(polarities) > 1
        result.append(
            ClaimCluster(
                representative=members[0],
                members=tuple(members),
                source_ids=tuple(dict.fromkeys(member.source for member in members)),
                conflict=conflict,
            )
        )
    return tuple(result)


def _polarity(text: str) -> str:
    lowered = text.lower()
    negation = re.search(r"\b(?:not|no|never|without|cannot|can't|didn't|doesn't|isn't|wasn't)\b", lowered)
    return "negative" if negation else "positive"


def _unresolved_questions(question: str, rounds: Sequence[OpenResearchRound], clusters: Sequence[ClaimCluster]) -> list[str]:
    gaps: list[str] = []
    if not rounds:
        gaps.append("No search round produced observations.")
    if not any(round.documents for round in rounds):
        gaps.append("No source documents were retrieved; search snippets are insufficient for deeper interpretation.")
    if not clusters:
        gaps.append("No candidate claims were extracted from acquired documents.")
    if any(cluster.conflict for cluster in clusters):
        gaps.append("At least one claim cluster contains lexical polarity conflict; independent verification is required.")
    if len({claim.source for cluster in clusters for claim in cluster.members}) < 2:
        gaps.append("Evidence diversity is weak because fewer than two source kinds were observed.")
    gaps.append(f"The current result is an evidence landscape for: {question}")
    return gaps
