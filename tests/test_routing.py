from cognitia.capabilities import Capability, CapabilityAvailability, SelfModel
from cognitia.routing import CognitiveRouter


def test_router_selects_required_capability_when_available() -> None:
    model = SelfModel()
    model.register(Capability(name="causal_inference", domain="causality", reliability=0.8))

    route = CognitiveRouter(model).route(
        required_capability="causal_inference",
        preferred_method="intervention analysis",
    )

    assert route.availability is CapabilityAvailability.AVAILABLE
    assert route.method == "intervention analysis"
    assert route.requires_qualification is False


def test_router_uses_explicit_weaker_fallback_when_required_capability_is_missing() -> None:
    model = SelfModel()
    model.register(Capability(name="correlation_analysis", domain="statistics", reliability=0.9))

    route = CognitiveRouter(model).route(
        required_capability="causal_inference",
        preferred_method="intervention analysis",
        fallback_capability="correlation_analysis",
        fallback_method="correlation analysis",
        substitution_note="Correlation can generate hypotheses but cannot establish causality.",
    )

    assert route.availability is CapabilityAvailability.MISSING
    assert route.substitution_required is True
    assert route.requires_qualification is True
    assert route.capability is not None
    assert "cannot establish causality" in route.limitation


def test_router_reports_unavailable_capability_without_fake_substitution() -> None:
    route = CognitiveRouter(SelfModel()).route(
        required_capability="counterfactual_reasoning",
        preferred_method="counterfactual simulation",
    )

    assert route.availability is CapabilityAvailability.MISSING
    assert route.substitution_required is False
    assert route.requires_qualification is True
    assert "counterfactual_reasoning" in route.limitation
