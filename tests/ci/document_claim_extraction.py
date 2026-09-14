from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation


def main() -> None:
    observation = EnvironmentObservation(
        id="document:kilogram",
        source="web:wikimedia:document",
        content=(
            "The kilogram was originally defined in terms of a physical artifact. "
            "In 2019, the definition was changed to use the Planck constant. "
            "Some historical accounts report that the artifact could drift over time."
        ),
        metadata=(("kind", "web-document"), ("url", "https://en.wikipedia.org/wiki/Kilogram")),
    )
    claims = DocumentClaimExtractor().extract(observation)
    assert len(claims) == 3, claims
    assert all(c.observation_id == observation.id for c in claims)
    assert all(c.source == observation.source for c in claims)
    assert any("2019" in c.temporal_markers for c in claims)
    assert any(c.uncertainty_markers for c in claims)
    assert any("changed" in c.relations for c in claims)
    assert all(c.proposition == c.sentence for c in claims)
    print("DOCUMENT_CLAIM_EXTRACTION_SUCCESS")


if __name__ == "__main__":
    main()
