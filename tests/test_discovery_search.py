from cognitia.discovery import ExplanatoryGap, HypothesisCandidate
from cognitia.discovery_experiments import DiscriminatingExperimentSelector
from cognitia.discovery_hypotheses import ExplanatoryModel, HypothesisSpaceBuilder, HypothesisTransform
from cognitia.discovery_prediction import PredictionDeriver


def gap() -> ExplanatoryGap:
    return ExplanatoryGap(("o1",), ("model misses condition-specific effect",))


def test_hypothesis_space_is_traceable_and_bounded() -> None:
    model = ExplanatoryModel(
        id="m1",
        proposition="output remains stable",
        assumptions=("condition is uniform", "measurement is unbiased"),
        variables=("temperature", "load"),
    )
    alternatives = HypothesisSpaceBuilder().build(
        model,
        gap(),
        missing_variables=("latency",),
    )
    assert alternatives
    assert all(item.source_model == "m1" for item in alternatives)
    assert all(item.novelty_status == "unassessed" for item in alternatives)
    assert {item.transform for item in alternatives} == set(HypothesisTransform)


def test_prediction_contract_and_discrimination() -> None:
    h1 = HypothesisCandidate("h1", "effect increases with load", ("o1",))
    h2 = HypothesisCandidate("h2", "effect stays stable with load", ("o1",))
    deriver = PredictionDeriver()
    p1 = deriver.derive(h1, condition="load=high", expected="increase", falsifier="no increase")
    p2 = deriver.derive(h2, condition="load=high", expected="stable", falsifier="increase")
    assert deriver.is_discriminating(p1, p2)
    experiment = DiscriminatingExperimentSelector().select((p1, p2))
    assert experiment is not None
    assert experiment.condition == "load=high"


def test_non_discriminating_predictions_do_not_create_experiment() -> None:
    h1 = HypothesisCandidate("h1", "same", ("o1",))
    h2 = HypothesisCandidate("h2", "also same", ("o1",))
    deriver = PredictionDeriver()
    p1 = deriver.derive(h1, condition="A", expected="x", falsifier="y")
    p2 = deriver.derive(h2, condition="A", expected="x", falsifier="y")
    assert DiscriminatingExperimentSelector().select((p1, p2)) is None
