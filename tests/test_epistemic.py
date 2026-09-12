import pytest

from cognitia.epistemic import (
    CapabilitySubstitution,
    EpistemicStatus,
    ReasoningResult,
    VerificationPlan,
)


def test_capability_limited_result_can_still_be_useful() -> None:
    result = ReasoningResult(
        claim="Redis overload is a plausible contributor to the outage.",
        status=EpistemicStatus.CAPABILITY_LIMITED,
        reasoning_method="correlation analysis",
        confidence=0.67,
        limitations=("Correlation does not establish causality.",),
        substitution=CapabilitySubstitution(
            required_capability="causal inference",
            available_capability="correlation analysis",
            purpose="generate candidate causal hypotheses",
            validity_limit="cannot establish intervention-level causality",
        ),
        verification=VerificationPlan(
            steps=("Run an intervention or controlled comparison.",),
            expected_value=0.9,
        ),
    )

    assert result.status is EpistemicStatus.CAPABILITY_LIMITED
    assert result.substitution is not None
    assert result.requires_verification is True


def test_capability_limited_result_requires_limitations() -> None:
    with pytest.raises(ValueError):
        ReasoningResult(
            claim="A candidate explanation.",
            status=EpistemicStatus.CAPABILITY_LIMITED,
            reasoning_method="pattern analysis",
            confidence=0.4,
        )


def test_verification_plan_requires_a_step() -> None:
    with pytest.raises(ValueError):
        VerificationPlan(steps=())


def test_substitution_is_not_allowed_on_established_result() -> None:
    substitution = CapabilitySubstitution(
        required_capability="causal inference",
        available_capability="correlation analysis",
        purpose="hypothesis generation",
        validity_limit="not causal proof",
    )

    with pytest.raises(ValueError):
        ReasoningResult(
            claim="A proved cause.",
            status=EpistemicStatus.ESTABLISHED,
            reasoning_method="correlation analysis",
            confidence=0.99,
            substitution=substitution,
        )
