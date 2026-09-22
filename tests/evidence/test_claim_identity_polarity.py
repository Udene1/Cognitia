from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.evidence.claim_identity import ClaimIdentityMatcher


def test_opposite_polarity_observations_share_underlying_identity():
    observations = (
        EnvironmentObservation(
            id="environment:positive",
            source="monitor_a",
            content="The service was healthy after restart.",
        ),
        EnvironmentObservation(
            id="environment:negative",
            source="monitor_b",
            content="The service was not healthy after restart.",
        ),
    )

    claims = DocumentClaimExtractor().extract_many(observations)
    identities = ClaimIdentityMatcher().match(claims)

    assert len(claims) == 2
    assert len(identities) == 1
    assert set(identities[0].matched_claim_ids) == {claim.id for claim in claims}
    assert "opposite_polarity" in identities[0].basis
    assert claims[0].polarity != claims[1].polarity
