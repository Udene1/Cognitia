"""Regression proof for historical three-digit dates in language semantics."""
from cognitia.language import build_language_frame


def main() -> None:
    frame = build_language_frame("Political instability weakened the Roman Empire in 476.")
    assert "476" in frame.temporal_markers
    assert frame.semantic_propositions[0].temporal_markers == ("476",)
    print("HISTORICAL_TEMPORAL_MARKER_SUCCESS")


if __name__ == "__main__":
    main()
