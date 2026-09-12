"""Extract language-independent computational structure from source code.

This is the first controlled step toward letting Cognitia learn from code without
being handed the intended solution logic. The extractor deliberately reasons
from executable structure (AST nodes, data flow, control flow, and aggregation
operations), not from comments or commit messages.

The result is a candidate representation, not proof that the abstraction is
correct. It must earn confidence through execution and transfer tests.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class ComputationalRepresentation:
    """Normalized computational structure inferred from source code."""

    language: str
    operations: tuple[str, ...]
    control_flow: tuple[str, ...]
    data_flow: tuple[str, ...]
    algorithm_family: str
    confidence: float
    epistemic_status: str = "inference"


class PythonCodeInterpreter:
    """Infer a bounded computational representation from Python source."""

    language = "python"

    def interpret(self, source: str) -> ComputationalRepresentation:
        if not source.strip():
            raise ValueError("source must not be empty")

        tree = ast.parse(source)
        operations: list[str] = []
        control_flow: list[str] = []
        data_flow: list[str] = []

        has_loop = False
        has_dict_accumulator = False
        has_get_default = False
        has_filter = False
        has_return = False
        has_comparison = False
        has_index_lookup = False

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                has_loop = True
                control_flow.append("iteration")
            elif isinstance(node, ast.If):
                control_flow.append("conditional")
                has_filter = True
            elif isinstance(node, ast.Return):
                has_return = True
            elif isinstance(node, ast.Compare):
                has_comparison = True
            elif isinstance(node, ast.Subscript):
                has_index_lookup = True
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "get" and len(node.args) >= 1:
                    has_get_default = True
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Subscript):
                        has_dict_accumulator = True
                        data_flow.append("update keyed state")
                    elif isinstance(target, ast.Name):
                        data_flow.append(f"assign {target.id}")
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Subscript):
                has_dict_accumulator = True
                data_flow.append("combine value into keyed state")

        if has_loop:
            operations.append("iterate records")
        if has_dict_accumulator:
            operations.append("maintain keyed accumulator")
        if has_get_default:
            operations.append("initialize missing key")
        if has_comparison:
            operations.append("compare values")
        if has_index_lookup:
            operations.append("read keyed field")
        if has_filter:
            operations.append("filter by condition")
        if has_return:
            operations.append("return result")

        if has_loop and has_dict_accumulator and has_get_default:
            algorithm_family = "group_by_reduce"
            confidence = 0.92
            data_flow.extend((
                "partition records by key",
                "combine values within each key",
                "emit one result per key",
            ))
        elif has_loop and has_filter and has_return:
            algorithm_family = "filter_selection"
            confidence = 0.82
        elif has_loop and has_index_lookup and has_comparison:
            algorithm_family = "linear_search"
            confidence = 0.78
        else:
            algorithm_family = "unknown"
            confidence = 0.35

        return ComputationalRepresentation(
            language=self.language,
            operations=tuple(dict.fromkeys(operations)),
            control_flow=tuple(dict.fromkeys(control_flow)),
            data_flow=tuple(dict.fromkeys(data_flow)),
            algorithm_family=algorithm_family,
            confidence=confidence,
        )
