from cognitia.capabilities import Capability, SelfModel
from cognitia.epistemic import EpistemicStatus, VerificationPlan
from cognitia.reasoning import qualify_attempt
from cognitia.routing import CognitiveRouter


def test_partial_route_produces_qualified_attempt() -> None:
    model = SelfModel()
    model.register(Capability(name="correlation_analysis", domain="statistics", reliability=0.9))
    route = CognitiveRouter(model).route(
        required_capability="causal_inference",
        preferred_method="intervention analysis",
        fallback_capability="correlation_analysis",
        fallback_method="correlation analysis",
    )

    attempt = qualify_attempt(
        claim="A may contribute to B.",
        route=route,
        confidence=0.65,
        supporting_evidence=("A preceded B repeatedly.",),
        verification=VerificationPlan(
            steps=("Run a controlled intervention on A.",),
            expected_value=0.9,
        ),
    )

    assert attempt.result.status is EpistemicStatus.CAPABILITY_LIMITED
    assert attempt.result.substitution is not None
    assert attempt.result.verification is not None


def test_missing_capability_does_not_invent_a_solution() -> None:
    route = CognitiveRouter(SelfModel()).route(
        required_capability="counterfactual_reasoning",
        preferred_method="counterfactual simulation",
    )

    attempt = qualify_attempt(
        claim="No justified conclusion yet.",
        route=route,
        confidence=0.1,
    )

    assert attempt.result.status is EpistemicStatus.UNRESOLVED
    assert attempt.result.substitution is None
    assert attempt.result.limitations
