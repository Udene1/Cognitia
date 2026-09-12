"""Extract language-independent computational structure from source code.

The extractor deliberately reasons from executable structure (AST nodes, data
data flow, control flow, and collection/reduction relationships), not from
comments or commit messages. The representation is a hypothesis about
computation, not proof of semantic equivalence.
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
        has_dict_comprehension = False
        has_reduction = False
        has_nested_iteration = False
        has_key_dependency = False

        parents = self._parent_map(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                has_loop = True
                control_flow.append("iteration")
                parent = parents.get(id(node))
                if isinstance(parent, (ast.For, ast.While)):
                    has_nested_iteration = True
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                control_flow.append("comprehension")
                if isinstance(node, ast.DictComp):
                    has_dict_comprehension = True
                    if any(isinstance(item, ast.GeneratorExp) for item in ast.walk(node.value)):
                        has_nested_iteration = True
                if len(node.generators) > 1:
                    has_nested_iteration = True
            elif isinstance(node, ast.If):
                control_flow.append("conditional")
                has_filter = True
            elif isinstance(node, ast.Return):
                has_return = True
            elif isinstance(node, ast.Compare):
                has_comparison = True
            elif isinstance(node, ast.Subscript):
                has_index_lookup = True
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "get" and len(node.args) >= 1:
                    has_get_default = True
                if isinstance(node.func, ast.Name) and node.func.id in {"sum", "reduce"}:
                    has_reduction = True
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

        if has_comparison and has_nested_iteration:
            has_key_dependency = self._has_cross_scope_key_dependency(tree)

        if has_loop or has_nested_iteration:
            operations.append("iterate records")
        if has_dict_accumulator:
            operations.append("maintain keyed accumulator")
        if has_get_default:
            operations.append("initialize missing key")
        if has_reduction:
            operations.append("reduce values")
        if has_comparison:
            operations.append("compare values")
        if has_index_lookup:
            operations.append("read keyed field")
        if has_filter:
            operations.append("filter by condition")
        if has_dict_comprehension:
            operations.append("construct keyed result")
        if has_key_dependency:
            data_flow.append("derive grouping key dependency")
        if has_return:
            operations.append("return result")

        if self._is_group_by_reduce(
            has_loop=has_loop,
            has_dict_accumulator=has_dict_accumulator,
            has_get_default=has_get_default,
            has_dict_comprehension=has_dict_comprehension,
            has_reduction=has_reduction,
            has_key_dependency=has_key_dependency,
        ):
            algorithm_family = "group_by_reduce"
            confidence = 0.92 if has_dict_accumulator else 0.88
            data_flow.extend(
                (
                    "partition records by key",
                    "combine values within each key",
                    "emit one result per key",
                )
            )
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

    @staticmethod
    def _is_group_by_reduce(
        *,
        has_loop: bool,
        has_dict_accumulator: bool,
        has_get_default: bool,
        has_dict_comprehension: bool,
        has_reduction: bool,
        has_key_dependency: bool,
    ) -> bool:
        """Recognize reduction from structural relationships, not field names."""
        imperative = has_loop and has_dict_accumulator and (has_get_default or has_reduction)
        declarative = has_dict_comprehension and has_reduction and has_key_dependency
        return imperative or declarative

    @staticmethod
    def _parent_map(root: ast.AST) -> dict[int, ast.AST]:
        parents: dict[int, ast.AST] = {}
        for parent in ast.walk(root):
            for child in ast.iter_child_nodes(parent):
                parents[id(child)] = parent
        return parents

    @staticmethod
    def _has_cross_scope_key_dependency(tree: ast.AST) -> bool:
        """Detect an outer-key dependency inside a nested reduction predicate."""
        for node in ast.walk(tree):
            if not isinstance(node, ast.DictComp) or not isinstance(node.key, ast.Name):
                continue
            key_name = node.key.id
            nested_generators = [item for item in ast.walk(node.value) if isinstance(item, ast.GeneratorExp)]
            for generator in nested_generators:
                if any(
                    isinstance(item, ast.Name) and item.id == key_name
                    for item in ast.walk(generator)
                    if item is not generator
                ):
                    return True
            for generator in node.generators:
                if any(isinstance(item, ast.Name) and item.id == key_name for item in ast.walk(generator.iter)):
                    return True
                for condition in generator.ifs:
                    if any(isinstance(item, ast.Name) and item.id == key_name for item in ast.walk(condition)):
                        return True
        return False
