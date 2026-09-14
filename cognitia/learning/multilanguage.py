"""Language adapters that map source code into one computational representation.

Cognitia does not compile source into a private programming language here. Each
adapter extracts executable structure and maps it into the same semantic IR so
cross-language transfer can be tested without an LLM.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .code_representation import ComputationalRepresentation, PythonCodeInterpreter


class JavaScriptCodeInterpreter:
    """Bounded structural interpreter for common JavaScript computations."""

    language = "javascript"

    def interpret(self, source: str) -> ComputationalRepresentation:
        if not source.strip():
            raise ValueError("source must not be empty")
        operations: list[str] = []
        control: list[str] = []
        data: list[str] = []
        loop = bool(re.search(r"\b(?:for|while)\b", source))
        keyed = bool(re.search(r"(?:\[\s*[^\]]+\s*\]|\.get\(|\?\?)", source))
        reduce_call = bool(re.search(r"\.reduce\s*\(", source))
        map_call = bool(re.search(r"\.map\s*\(", source))
        filter_call = bool(re.search(r"\.filter\s*\(", source))
        object_acc = bool(re.search(r"(?:const|let|var)\s+\w+\s*=\s*\{\s*\}", source))
        return_seen = bool(re.search(r"\breturn\b", source))
        conditional = bool(re.search(r"\bif\b|\?", source))
        grouping = bool(re.search(r"\b(?:key|group|customer|category|account|name)\b", source, re.I))
        addition = bool(re.search(r"\+=|\+\s*amount|sum|total", source, re.I))

        if loop or map_call or reduce_call:
            operations.append("iterate records")
            control.append("iteration")
        if conditional or filter_call:
            control.append("conditional")
            operations.append("filter by condition") if filter_call else None
        if object_acc or keyed:
            operations.append("maintain keyed accumulator")
            data.append("update keyed state")
        if reduce_call or addition:
            operations.append("reduce values")
        if keyed:
            operations.append("read keyed field")
        if return_seen:
            operations.append("return result")

        if (loop and object_acc and addition) or (reduce_call and grouping and addition):
            family = "group_by_reduce"
            confidence = 0.84
            data.extend(("partition records by key", "combine values within each key", "emit one result per key"))
        elif filter_call:
            family = "filter_selection"
            confidence = 0.82
        elif loop and keyed:
            family = "linear_search"
            confidence = 0.72
        else:
            family = "unknown"
            confidence = 0.35
        return ComputationalRepresentation("javascript", tuple(dict.fromkeys(operations)), tuple(dict.fromkeys(control)), tuple(dict.fromkeys(data)), family, confidence)


class SQLCodeInterpreter:
    """Bounded structural interpreter for SELECT/GROUP BY computations."""

    language = "sql"

    def interpret(self, source: str) -> ComputationalRepresentation:
        if not source.strip():
            raise ValueError("source must not be empty")
        text = re.sub(r"\s+", " ", source.lower()).strip()
        operations: list[str] = []
        control: list[str] = []
        data: list[str] = []
        grouped = bool(re.search(r"\bgroup\s+by\b", text))
        aggregate = bool(re.search(r"\b(sum|count|avg|min|max)\s*\(", text))
        where = bool(re.search(r"\bwhere\b", text))
        join = bool(re.search(r"\bjoin\b", text))
        if "select" in text:
            operations.append("select fields")
        if grouped:
            operations.append("partition records by key")
            control.append("grouping")
            data.append("derive grouping key dependency")
        if aggregate:
            operations.append("reduce values")
            data.append("combine values within each key")
        if where:
            operations.append("filter by condition")
            control.append("conditional")
        if join:
            operations.append("join relations")
            data.append("match records across relations")
        if grouped and aggregate:
            operations.append("emit one result per key")
            family = "group_by_reduce"
            confidence = 0.95
        elif where:
            family = "filter_selection"
            confidence = 0.84
        else:
            family = "unknown"
            confidence = 0.4
        return ComputationalRepresentation("sql", tuple(dict.fromkeys(operations)), tuple(dict.fromkeys(control)), tuple(dict.fromkeys(data)), family, confidence)


@dataclass(frozen=True)
class MultiLanguageCodeInterpreter:
    """Dispatch source through language-specific adapters into one IR."""

    python: PythonCodeInterpreter = PythonCodeInterpreter()
    javascript: JavaScriptCodeInterpreter = JavaScriptCodeInterpreter()
    sql: SQLCodeInterpreter = SQLCodeInterpreter()

    def interpret(self, source: str, *, language: str) -> ComputationalRepresentation:
        normalized = language.lower().replace("js", "javascript")
        if normalized == "python":
            return self.python.interpret(source)
        if normalized == "javascript":
            return self.javascript.interpret(source)
        if normalized == "sql":
            return self.sql.interpret(source)
        raise ValueError(f"unsupported source language: {language}")
