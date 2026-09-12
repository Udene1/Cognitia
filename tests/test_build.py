import pytest

from cognitia.build import CapabilityRecord, create_build


def test_build_manifest_is_immutable_and_tracks_parent():
    build = create_build(
        "C0.2",
        "0.1.0",
        [CapabilityRecord("physics", "experimental"), CapabilityRecord("memory", "foundation")],
        parent_build="C0.1",
    )

    assert build.build_id == "C0.2"
    assert build.parent_build == "C0.1"
    assert build.has_capability("physics")
    assert len(build.active_capabilities()) == 2


def test_build_requires_unique_capabilities():
    with pytest.raises(ValueError, match="unique"):
        create_build(
            "C0.2",
            "0.1.0",
            [CapabilityRecord("memory", "foundation"), CapabilityRecord("memory", "experimental")],
        )


def test_candidate_capability_is_not_active():
    build = create_build(
        "C0.2-candidate",
        "0.1.0",
        [
            CapabilityRecord("memory", "foundation"),
            CapabilityRecord("causal_inference", "candidate", status="candidate"),
        ],
    )

    assert not build.has_capability("causal_inference")
    assert [c.name for c in build.active_capabilities()] == ["memory"]
