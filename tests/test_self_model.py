from cognitia.capabilities import Capability, SelfModel
from cognitia.self_model import CapabilityHistory, CapabilityOutcome, update_self_model


def test_self_model_reliability_learns_from_outcomes() -> None:
    model = SelfModel()
    model.register(
        Capability(
            name="pattern_analysis",
            domain="reasoning",
            reliability=0.5,
        )
    )
    history = CapabilityHistory()
    history.record(CapabilityOutcome("pattern_analysis", True, context="A"))
    history.record(CapabilityOutcome("pattern_analysis", True, context="B"))
    history.record(
        CapabilityOutcome(
            "pattern_analysis",
            False,
            context="hidden-variable case",
            failure_mode="confuses correlation with causation",
        )
    )

    revised = update_self_model(model, history, "pattern_analysis")

    assert revised is not None
    assert revised.reliability == 2 / 3
    assert "confuses correlation with causation" in revised.failure_modes


def test_failed_outcome_requires_failure_mode() -> None:
    import pytest

    with pytest.raises(ValueError):
        CapabilityOutcome("reasoning", False)


def test_no_history_does_not_change_capability() -> None:
    model = SelfModel()
    original = Capability(name="reasoning", domain="general", reliability=0.8)
    model.register(original)

    assert update_self_model(model, CapabilityHistory(), "reasoning") == original
