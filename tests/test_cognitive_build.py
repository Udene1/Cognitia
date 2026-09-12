from cognitia.cognitive_build import CapabilityManifest, CapabilityState, CognitiveBuild


def test_candidate_can_be_held_without_deleting_it():
    build = CognitiveBuild("C0.2", "0.1.0", (CapabilityManifest("physics", CapabilityState.ACTIVE, 0.9),))
    candidate = CapabilityManifest("causal_inference", CapabilityState.CANDIDATE, 0.4, "C0.2")
    next_build = build.with_candidate(candidate).hold("causal_inference")
    assert next_build.capability("causal_inference") is not None
    assert next_build.capability("causal_inference").state is CapabilityState.HELD
    assert build.capability("causal_inference") is None


def test_candidate_can_be_promoted_without_mutating_parent_snapshot():
    build = CognitiveBuild("C0.2", "0.1.0", (CapabilityManifest("physics", CapabilityState.ACTIVE, 0.9),))
    candidate = CapabilityManifest("causal_inference", CapabilityState.CANDIDATE, 0.8, "C0.2")
    candidate_build = build.with_candidate(candidate).promote("causal_inference")
    assert candidate_build.capability("causal_inference").state is CapabilityState.ACTIVE
    assert build.capability("causal_inference") is None
