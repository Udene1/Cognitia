"""Extract transferable decision logic instead of only named concepts."""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass

from ..logic_ir import LogicModel, LogicNode, LogicRelation, model_from_parts
from .code_representation import PythonCodeInterpreter


@dataclass(frozen=True)
class ConceptualRepresentation:
    family: str
    logic: tuple[str, ...]
    confidence: float
    epistemic_status: str = "inference"
    model: LogicModel | None = None


class GenericLogicExtractor:
    """Extract role/order/constraint structure from executable reasoning."""

    def extract_python(self, source: str, *, source_id: str = "python") -> LogicModel:
        if not source.strip():
            raise ValueError("source must not be empty")
        tree = ast.parse(source)
        nodes: list[LogicNode] = []
        relations: list[LogicRelation] = []
        index = 0
        previous: str | None = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Return, ast.Assign, ast.AugAssign, ast.Compare)):
                role = {
                    ast.If: "condition", ast.For: "iteration", ast.While: "iteration",
                    ast.Return: "outcome", ast.Assign: "state_update", ast.AugAssign: "state_update",
                    ast.Compare: "constraint",
                }.get(type(node), "operation")
                node_id = f"logic:{index}"
                index += 1
                nodes.append(LogicNode(node_id, role, type(node).__name__))
                if previous:
                    relations.append(LogicRelation(previous, "precedes", node_id))
                previous = node_id
                if isinstance(node, ast.If) and node.body:
                    # The guard constrains the first operation in its body; do not
                    # fabricate a self-edge merely to record that a guard exists.
                    body = node.body[0]
                    body_id = f"logic:guard-body:{index}"
                    nodes.append(LogicNode(body_id, "guarded_operation", type(body).__name__))
                    relations.append(LogicRelation(node_id, "guards", body_id))
                    index += 1
        invariants = _infer_invariants(tree)
        purpose = "decision procedure" if any(n.role == "condition" for n in nodes) else "computational procedure"
        return model_from_parts(purpose=purpose, nodes=nodes, relations=relations,
                                invariants=invariants, source_artifacts=(source_id,),
                                source_representations=("python",),
                                interpretation="AST operations projected into role/order/constraint structure")


class TradeoffBalanceInterpreter:
    """Compatibility interpreter backed by generic logic extraction."""

    def __init__(self, interpreter: PythonCodeInterpreter | None = None) -> None:
        self._interpreter = interpreter or PythonCodeInterpreter()
        self._extractor = GenericLogicExtractor()

    def interpret(self, source: str) -> ConceptualRepresentation:
        base = self._interpreter.interpret(source)
        model = self._extractor.extract_python(source)
        tree = ast.parse(source)
        conditional_count = sum(isinstance(node, ast.If) for node in ast.walk(tree))
        comparison_count = sum(isinstance(node, ast.Compare) for node in ast.walk(tree))
        has_return = "return result" in base.operations
        if conditional_count >= 2 and comparison_count >= 2 and has_return:
            return ConceptualRepresentation(
                family="tradeoff_balance",
                logic=("evaluate competing outcomes", "preserve the baseline when an improvement carries a regression",
                       "adopt the improvement when the regression is resolved"),
                confidence=0.70, model=model,
            )
        return ConceptualRepresentation("unknown", base.operations, 0.35, model=model)

    @staticmethod
    def infer_problem_signature(problem: str) -> tuple[str, ...]:
        words = set(re.findall(r"[a-z]+", problem.lower()))
        improvement = bool({"improves", "improve", "benefit", "gain", "better", "growth"} & words)
        regression = bool({"worsens", "worse", "cost", "downside", "inflation", "risk", "regression"} & words)
        decision = bool({"policy", "decision", "adopt", "adoption", "change", "strategy"} & words)
        if improvement and regression and decision:
            return ("tradeoff_balance",)
        return ("unknown",)


def _infer_invariants(tree: ast.AST) -> tuple[str, ...]:
    invariants: list[str] = []
    if any(isinstance(n, ast.Return) for n in ast.walk(tree)):
        invariants.append("procedure must produce an explicit outcome")
    if any(isinstance(n, ast.If) for n in ast.walk(tree)):
        invariants.append("outcome is constrained by a condition")
    if any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree)):
        invariants.append("state is transformed across repeated elements")
    if any(isinstance(n, ast.Compare) for n in ast.walk(tree)):
        invariants.append("decision depends on a comparison constraint")
    return tuple(invariants)
