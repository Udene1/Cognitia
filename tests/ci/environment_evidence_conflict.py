"""Test whether contradiction can emerge from ordinary environment evidence."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.evidence.claim_identity import ClaimIdentityMatcher
from cognitia.evidence.convergence import EvidenceConvergenceEngine
from cognitia.evidence.model import Claim, EvidenceRecord, EvidenceSource, SourceLineage

OBSERVATIONS = (
    EnvironmentObservation(
        id="environment:service-a",
        source="independent_monitor_a",
        content="The service was healthy after restart.",
        observed_at="2026-09-17T17:00:00Z",
        metadata={"source_kind": "monitor"},
    ),
    EnvironmentObservation(
        id="environment:service-b",
        source="independent_monitor_b",
        content="The service was not healthy after restart.",
        observed_at="2026-09-17T17:00:05Z",
        metadata={"source_kind": "monitor"},
    ),
)


def main() -> None:
    extractor = DocumentClaimExtractor()
    claims = extractor.extract_many(OBSERVATIONS)
    identities = ClaimIdentityMatcher().match(claims)

    evidence: list[EvidenceRecord] = []
    identity_records: list[dict[str, object]] = []
    for identity in identities:
        matched = tuple(item for item in claims if item.id in identity.matched_claim_ids)
        identity_records.append({
            "claim_id": identity.claim_id,
            "canonical_key": identity.canonical_key,
            "matched_claim_ids": list(identity.matched_claim_ids),
            "confidence": identity.confidence,
            "basis": list(identity.basis),
        })
        representative = matched[0]
        claim = Claim(
            id=identity.claim_id,
            proposition=representative.proposition,
            domain="systemic",
        )
        for item in matched:
            evidence.append(EvidenceRecord(
                id=f"evidence:{item.observation_id}",
                claim_id=claim.id,
                source=EvidenceSource(
                    id=item.source,
                    kind="environment",
                    name=item.source,
                    reliability=0.8,
                ),
                content=item.sentence,
                supports=item.polarity != "negative",
                lineage=SourceLineage(source_id=item.source),
                observation_id=item.observation_id,
                measured_at=next(obs.observed_at for obs in OBSERVATIONS if obs.id == item.observation_id),
                method="document_claim_extraction",
            ))

    assessments = []
    convergence = EvidenceConvergenceEngine()
    for identity in identities:
        representative = next(item for item in claims if item.id == identity.claim_id)
        claim = Claim(id=identity.claim_id, proposition=representative.proposition, domain="systemic")
        assessment = convergence.assess(claim, tuple(evidence))
        assessments.append({
            "claim_id": claim.id,
            "claim": claim.proposition,
            "supporting": list(assessment.supporting),
            "contradicting": list(assessment.contradicting),
            "independent_support_groups": assessment.independent_support_groups,
            "independent_contradiction_groups": assessment.independent_contradiction_groups,
            "weighted_support": assessment.weighted_support,
            "weighted_contradiction": assessment.weighted_contradiction,
            "status": assessment.status,
        })

    artifact = {
        "experiment": "environment-evidence-conflict",
        "research_question": "Can incompatible observations produce a conflicted evidence state through the ordinary observation -> claim identity -> evidence -> convergence path, without an explicit epistemic outcome?",
        "handholding": {
            "expected_conflict": None,
            "expected_claim_identity": None,
            "expected_status": None,
            "expected_action": None,
        },
        "observations": [
            {"id": item.id, "source": item.source, "content": item.content}
            for item in OBSERVATIONS
        ],
        "extracted_claims": [
            {
                "id": item.id,
                "proposition": item.proposition,
                "observation_id": item.observation_id,
                "polarity": item.polarity,
                "relations": list(item.relations),
                "entities": list(item.entities),
            }
            for item in claims
        ],
        "identities": identity_records,
        "assessments": assessments,
        "comparison": {
            "multiple_observations": len(OBSERVATIONS) == 2,
            "claims_extracted": bool(claims),
            "identity_group_contains_both": any(len(item["matched_claim_ids"]) == 2 for item in identity_records),
            "conflicted_status_observed": any(item["status"] == "conflicted" for item in assessments),
            "contradiction_groups_observed": any(item["independent_contradiction_groups"] > 0 for item in assessments),
        },
    }
    path = Path(".ci/environment-evidence-conflict.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
