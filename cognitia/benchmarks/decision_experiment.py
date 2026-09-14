"""Capability benchmark for choosing and using a discriminating experiment.

The test is deliberately outcome-oriented: Cognitia must select an experiment
that separates competing predictions, observe a simulated result, and update
the surviving hypothesis instead of merely constructing an experiment object.
"""
from __future__ import annotations

from dataclasses import dataclass

from cognitia.discovery_experiments import DiscriminatingExperimentSelector, Experiment
from cognitia.discovery_prediction import Prediction


@dataclass(frozen=True)
class DecisionProblem:
    id: str
    predictions: tuple[Prediction, ...]
    observed_outcome: str
    expected_experiment_id: str
    expected_survivor: str


@dataclass(frozen=True)
class DecisionTrace:
    problem_id: str
    selected_experiment: str | None
    expected_information_gain: float
    observed_outcome: str
    surviving_hypothesis: str | None
    rejected_hypotheses: tuple[str, ...]
    capability_used: bool


class ExperimentDecisionSolver:
    def __init__(self) -> None:
        self.selector = DiscriminatingExperimentSelector()

    def solve(self, problem: DecisionProblem) -> DecisionTrace:
        experiment = self.selector.select(problem.predictions)
        if experiment is None:
            return DecisionTrace(problem.id, None, 0.0, problem.observed_outcome, None, (), False)
        matching = tuple(p for p in experiment.predictions if p.expected == problem.observed_outcome)
        survivor = matching[0].hypothesis_id if len(matching) == 1 else None
        rejected = tuple(p.hypothesis_id for p in experiment.predictions if p.expected != problem.observed_outcome)
        return DecisionTrace(
            problem.id,
            experiment.id,
            experiment.expected_information_gain,
            problem.observed_outcome,
            survivor,
            rejected,
            survivor is not None and experiment.expected_information_gain > 0,
        )


class DecisionExperimentBenchmark:
    def __init__(self, problems: tuple[DecisionProblem, ...] | None = None) -> None:
        self.problems = problems or decision_problems()
        self.solver = ExperimentDecisionSolver()

    def run(self) -> tuple[tuple[DecisionProblem, DecisionTrace, bool], ...]:
        results = []
        for problem in self.problems:
            trace = self.solver.solve(problem)
            passed = (
                trace.selected_experiment == problem.expected_experiment_id
                and trace.surviving_hypothesis == problem.expected_survivor
                and trace.capability_used
                and problem.observed_outcome in {p.expected for p in problem.predictions}
            )
            results.append((problem, trace, passed))
        return tuple(results)


def decision_problems() -> tuple[DecisionProblem, ...]:
    condition = "run service with dependency isolated"
    a = Prediction("cache:p1", "cache-failure", condition, "latency remains high", "latency falls")
    b = Prediction("network:p1", "network-failure", condition, "latency falls", "latency remains high")
    c = Prediction("unrelated:p1", "unrelated-failure", "different condition", "latency remains high", "latency falls")
    return (
        DecisionProblem(
            "latency-cause",
            (a, b, c),
            "latency falls",
            "experiment:cache:p1:network:p1",
            "network-failure",
        ),
    )


def format_results(results: tuple[tuple[DecisionProblem, DecisionTrace, bool], ...]) -> str:
    lines = ["DISCRIMINATING_EXPERIMENT_PROBLEM_SUCCESS"]
    for problem, trace, passed in results:
        lines.append(f"PROBLEM: {problem.id} PASS={passed}")
        lines.append(f"  selected_experiment: {trace.selected_experiment}")
        lines.append(f"  information_gain: {trace.expected_information_gain:.3f}")
        lines.append(f"  observation: {trace.observed_outcome}")
        lines.append(f"  surviving_hypothesis: {trace.surviving_hypothesis}")
        lines.append(f"  rejected_hypotheses: {list(trace.rejected_hypotheses)}")
    lines.append(f"PASSED: {sum(passed for _, _, passed in results)}/{len(results)}")
    return "\n".join(lines)
