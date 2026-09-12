import pytest

from cognitia.acquisition import (
    AcquisitionStage,
    CapabilityRequirement,
    propose_capability_acquisition,
)


def requirement() -> CapabilityRequirement:
    return CapabilityRequirement(
        name="causal_inference",
        domain="causality",
        reason="Repeated correlation-only attempts cannot establish intervention effects.",
        evidence=("three failed causal investigations",),
        required_inputs=("observations", "candidate_graph"),
        expected_outputs=("causal_hypotheses", "intervention_predictions"),
    )


def test_proposal_is_explicitly_non_deploying() -> None:
    proposal = propose_capability_acquisition(
        requirement(),
        representation="causal graph with intervention semantics",
        acquisition_steps=("define graph representation", "implement intervention evaluator"),
        tests=("reject cyclic assumptions where unsupported",),
        benchmarks=("held-out intervention cases",),
        safety_constraints=("sandbox execution", "no automatic deployment"),
    )

    assert proposal.stage is AcquisitionStage.PROPOSED
    assert proposal.requirement.name == "causal_inference"


def test_proposal_progression_is_immutable() -> None:
    proposal = propose_capability_acquisition(
        requirement(),
        representation="causal graph",
        acquisition_steps=("implement",),
        tests=("unit tests",),
        benchmarks=("benchmark suite",),
        safety_constraints=("sandbox",),
    )

    tested = proposal.advance(AcquisitionStage.TESTED)

    assert proposal.stage is AcquisitionStage.PROPOSED
    assert tested.stage is AcquisitionStage.TESTED


@pytest.mark.parametrize(
    "field",
    ["representation", "acquisition_steps", "tests", "benchmarks", "safety_constraints"],
)
def test_proposal_requires_validation_artifacts(field: str) -> None:
    kwargs = dict(
        representation="representation",
        acquisition_steps=("implement",),
        tests=("test",),
        benchmarks=("benchmark",),
        safety_constraints=("sandbox",),
    )
    kwargs[field] = () if field != "representation" else ""

    with pytest.raises(ValueError):
        propose_capability_acquisition(requirement(), **kwargs)
