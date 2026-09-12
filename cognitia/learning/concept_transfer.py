"""Cross-domain transfer from computational structure to abstract decisions."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .code_representation import ComputationalRepresentation, PythonCodeInterpreter


@dataclass(frozen=True)
class ConceptualRepresentation:
    family: str
    logic: tuple[str, ...]
    confidence: float
    epistemic_status: str = "inference"


class TradeoffBalanceInterpreter:
    """Infer a generic tradeoff policy from executable decision structure."""

    def __init__(self, interpreter: PythonCodeInterpreter | None = None) -> None:
        self._interpreter = interpreter or PythonCodeInterpreter()

    def interpret(self, source: str) -> ConceptualRepresentation:
        base = self._interpreter.interpret(source)
        conditional_count = base.control_flow.count("conditional")
        comparison = "compare values" in base.operations
        has_return = "return result" in base.operations
        if conditional_count >= 2 and comparison and has_return:
            return ConceptualRepresentation(
                family="tradeoff_balance",
                logic=(
                    "evaluate competing outcomes",
                    "preserve the baseline when an improvement carries a regression",
                    "adopt the improvement when the regression is resolved",
                ),
                confidence=0.70,
            )
        return ConceptualRepresentation("unknown", base.operations, 0.35)

    @staticmethod
    def infer_problem_signature(problem: str) -> tuple[str, ...]:
        """Map a new-domain description to an abstract decision structure."""
        words = set(re.findall(r"[a-z]+", problem.lower()))
        improvement = bool({"improves", "improve", "benefit", "gain", "better", "growth"} & words)
        regression = bool({"worsens", "worse", "cost", "downside", "inflation", "risk", "regression"} & words)
        decision = bool({"policy", "decision", "adopt", "adoption", "change", "strategy"} & words)
        if improvement and regression and decision:
            return ("tradeoff_balance",)
        return ("unknown",)
