"""Learn solution patterns directly from executable source code."""
from __future__ import annotations

import re

from cognitia.memory import Experience, Outcome

from .code_representation import ComputationalRepresentation, PythonCodeInterpreter


class CodeSolutionLearner:
    """Turn a problem + actual code + outcome into learned solution experience.

    The intended logic, implementation name, and problem signature are not
    supplied. They are derived from the code representation. This keeps the
    training path honest: the source program is the evidence from which the
    computational pattern is inferred.
    """

    def __init__(self, interpreter: PythonCodeInterpreter | None = None) -> None:
        self._interpreter = interpreter or PythonCodeInterpreter()

    def interpret(self, source: str) -> ComputationalRepresentation:
        return self._interpreter.interpret(source)

    def experience(
        self,
        *,
        problem: str,
        source: str,
        outcome_kind: str,
        outcome_description: str,
        context: dict[str, object] | None = None,
    ) -> Experience:
        representation = self.interpret(source)
        logic = self._logic_from(representation)
        return Experience(
            context={
                "solution_problem": problem,
                "solution_logic": logic,
                "solution_implementation": representation.algorithm_family,
                "solution_language": representation.language,
                "problem_signature": (representation.algorithm_family,),
                "representation_confidence": representation.confidence,
                **(context or {}),
            },
            action="infer computational solution from source",
            observation={
                "operations": representation.operations,
                "control_flow": representation.control_flow,
                "data_flow": representation.data_flow,
                "algorithm_family": representation.algorithm_family,
            },
            outcome=Outcome(outcome_kind, outcome_description),
        )

    @staticmethod
    def infer_problem_signature(problem: str) -> tuple[str, ...]:
        """Extract a small semantic signature from a natural-language problem.

        This is intentionally bounded rather than pretending to understand all
        language. It provides a real no-LLM transfer experiment: the target
        problem is not handed a signature by the test author.
        """
        words = set(re.findall(r"[a-z]+", problem.lower()))
        if ({"each", "per"} & words) and ({"total", "sum", "spending", "amounts"} & words):
            return ("group_by_reduce",)
        if {"only", "matching", "filter", "select"} & words:
            return ("filter_selection",)
        if {"find", "search", "locate"} & words:
            return ("linear_search",)
        return ("unknown",)

    @staticmethod
    def _logic_from(representation: ComputationalRepresentation) -> tuple[str, ...]:
        if representation.algorithm_family == "group_by_reduce":
            return (
                "partition records by key",
                "combine values within each key",
                "emit one result per key",
            )
        if representation.algorithm_family == "filter_selection":
            return (
                "inspect each record",
                "retain records satisfying a condition",
                "return selected records",
            )
        if representation.algorithm_family == "linear_search":
            return (
                "inspect records sequentially",
                "compare the target condition",
                "return the matching result",
            )
        return representation.operations
