import pytest

from cognitia.capabilities import (
    Capability,
    CapabilityAvailability,
    CapabilityGap,
    SelfModel,
)


def test_self_model_registers_and_assesses_capability() -> None:
    model = SelfModel()
    physics = Capability(
        name="dimensional_reasoning",
        domain="physics",
        reliability=0.9,
        maturity="stable",
    )

    model.register(physics)
    assessment = model.assess("dimensional_reasoning")

    assert assessment.availability is CapabilityAvailability.AVAILABLE
    assert assessment.capability == physics


def test_missing_capability_is_explicit_gap() -> None:
    assessment = SelfModel().assess("causal_inference")

    assert assessment.availability is CapabilityAvailability.MISSING
    assert assessment.gap is not None
    assert assessment.gap.required == "causal_inference"
    assert assessment.gap.substitution_allowed is False


def test_partial_capability_can_be_explicitly_substituted() -> None:
    gap = CapabilityGap(
        required="causal_inference",
        availability=CapabilityAvailability.PARTIAL,
        available_capability="correlation_analysis",
        substitution_allowed=True,
        substitution_note="Use correlation only to generate candidate hypotheses.",
    )

    assert gap.available_capability == "correlation_analysis"
    assert gap.substitution_allowed is True


def test_invalid_reliability_is_rejected() -> None:
    with pytest.raises(ValueError):
        Capability(name="bad", domain="test", reliability=1.1)


def test_domain_filter_returns_matching_capabilities() -> None:
    model = SelfModel(
        {
            "physics": Capability(name="physics", domain="physics"),
            "logic": Capability(name="logic", domain="reasoning"),
        }
    )

    assert model.capabilities_for_domain("physics") == (model.get("physics"),)
