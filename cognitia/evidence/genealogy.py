"""Evidence genealogy: count origins, not appearances.

Candidate claims are not independent evidence merely because they are separate
sentences or pages. This module keeps the distinction explicit: many findings
can descend from one observation/source root, and unknown provenance is never
upgraded to independence.
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from typing import Mapping, Sequence

from ..document_claims import ExtractedClaim
from ..environment import EnvironmentObservation


@dataclass(frozen=True)
class EvidenceOrigin:
    root_id: str
    source: str
    observation_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    finding_count: int
    independence: str


@dataclass(frozen=True)
class GenealogyAssessment:
    origins: tuple[EvidenceOrigin, ...]
    derivative_links: tuple[tuple[str, str, float], ...]
    finding_count: int
    observed_origin_count: int
    candidate_independent_origin_count: int
    unknown_origin_count: int

    @property
    def effective_independent_count(self) -> int:
        return self.candidate_independent_origin_count


class EvidenceGenealogyBuilder:
    """Build a conservative source-origin graph from acquired documents."""

    def assess(
        self,
        observations: Sequence[EnvironmentObservation],
        claims: Sequence[ExtractedClaim],
    ) -> GenealogyAssessment:
        by_id = {observation.id: observation for observation in observations}
        grouped: dict[str, list[ExtractedClaim]] = {}
        source_names: dict[str, str] = {}
        observation_ids: dict[str, list[str]] = {}
        unknown = 0

        for claim in claims:
            observation = by_id.get(claim.observation_id)
            if observation is None:
                unknown += 1
                continue
            metadata = dict(observation.metadata)
            root = metadata.get("origin_id") or metadata.get("url") or observation.id
            grouped.setdefault(root, []).append(claim)
            source_names[root] = observation.source
            observation_ids.setdefault(root, []).append(observation.id)

        origins = tuple(
            EvidenceOrigin(
                root_id=root,
                source=source_names[root],
                observation_ids=tuple(dict.fromkeys(observation_ids[root])),
                claim_ids=tuple(claim.id for claim in members),
                finding_count=len(members),
                independence="candidate_independent" if root else "unknown",
            )
            for root, members in grouped.items()
        )

        links: list[tuple[str, str, float]] = []
        roots = list(grouped)
        for index, left in enumerate(roots):
            left_text = " ".join(claim.proposition for claim in grouped[left])
            for right in roots[index + 1:]:
                right_text = " ".join(claim.proposition for claim in grouped[right])
                similarity = _token_similarity(left_text, right_text)
                if similarity >= 0.86:
                    links.append((left, right, round(similarity, 3)))

        derivative_roots = {root for left, right, _ in links for root in (left, right)}
        candidate_independent = len(origins) - len(derivative_roots)
        return GenealogyAssessment(
            origins=origins,
            derivative_links=tuple(links),
            finding_count=len(claims),
            observed_origin_count=len(origins),
            candidate_independent_origin_count=max(0, candidate_independent),
            unknown_origin_count=unknown,
        )


def _token_similarity(left: str, right: str) -> float:
    def normalize(value: str) -> str:
        return " ".join(re.findall(r"[a-z0-9]+", value.lower()))
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()
