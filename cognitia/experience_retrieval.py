"""Open-ended retrieval from durable observation experience.

The caller supplies a question, not a preselected history slice. Retrieval searches
the retained observation ledger and returns the evidence that best addresses the
question. Retrieval is intentionally deterministic and auditable; it does not
generate knowledge or require an LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .memory.observation_sqlite import SQLiteObservationStore
from .observation import Observation


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do", "does",
    "for", "from", "how", "in", "is", "it", "of", "on", "or", "should",
    "the", "to", "what", "when", "why", "with", "would", "next", "about",
}


@dataclass(frozen=True)
class ExperienceMatch:
    observation_id: str
    score: float
    matched_terms: tuple[str, ...]


class ObservationExperienceRetriever:
    """Select relevant retained experience from an observation ledger."""

    def retrieve(
        self,
        store: SQLiteObservationStore,
        question: str,
        *,
        environment: str | None = None,
        exclude_ids: Iterable[str] = (),
        limit: int = 12,
    ) -> tuple[ExperienceMatch, ...]:
        if not question.strip():
            raise ValueError("question is required")
        if limit < 1:
            raise ValueError("limit must be positive")

        terms = _terms(question)
        excluded = set(exclude_ids)
        observations = store.by_environment(environment) if environment else store.all()

        scored: list[ExperienceMatch] = []
        for observation in observations:
            if observation.id in excluded:
                continue
            text = " ".join(
                (
                    observation.kind,
                    observation.subject,
                    observation.payload,
                    " ".join(value for _, value in observation.metadata),
                )
            ).lower()
            matched = tuple(sorted(term for term in terms if re.search(rf"\b{re.escape(term)}\b", text)))
            if not matched:
                continue
            # Coverage is primary. A small recency term prevents identical
            # coverage from being decided arbitrarily while keeping retrieval
            # deterministic.
            coverage = len(matched) / len(terms)
            recency = _recency_score(observation)
            score = round(coverage + (0.05 * recency), 6)
            scored.append(ExperienceMatch(observation.id, score, matched))

        scored.sort(key=lambda item: (-item.score, item.observation_id))
        return tuple(scored[:limit])


def _terms(question: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                token.lower()
                for token in re.findall(r"[A-Za-z0-9]+", question)
                if len(token) > 2 and token.lower() not in _STOPWORDS
            }
        )
    )


def _recency_score(observation: Observation) -> float:
    # Timestamp ordering is already represented in the source data. This bounded
    # tie-break contribution rewards observations that actually carry timestamps
    # without pretending timestamp recency is semantic relevance.
    return 1.0 if observation.observed_at else 0.0
