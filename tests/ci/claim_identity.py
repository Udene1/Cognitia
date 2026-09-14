from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.evidence.claim_identity import ClaimIdentityMatcher


def main() -> None:
    extractor = DocumentClaimExtractor()
    docs = (
        EnvironmentObservation(id="a", source="web:a", content="The Roman Empire was weakened by political instability in 476."),
        EnvironmentObservation(id="b", source="web:b", content="Political instability weakened the Roman Empire in 476."),
        EnvironmentObservation(id="c", source="web:c", content="In 2019, political instability weakened the Roman Empire."),
    )
    claims = tuple(c for doc in docs for c in extractor.extract(doc))
    matcher = ClaimIdentityMatcher()
    identities = matcher.match(claims, threshold=0.70)
    assert len(claims) == 3, claims
    assert any(len(identity.matched_claim_ids) == 2 for identity in identities)
    score, basis = matcher.score(claims[0], claims[2])
    assert score < 0.78
    assert "temporal_mismatch" in basis
    print("CLAIM_IDENTITY_SUCCESS")
    print(f"claims={len(claims)} identities={len(identities)}")
    print(f"temporal_mismatch_score={score}")


if __name__ == "__main__":
    main()
