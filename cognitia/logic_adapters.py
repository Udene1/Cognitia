"""Adapters from existing representations into the common logic substrate."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .logic_ir import LogicModel, LogicNode, LogicRelation, model_from_parts
from .language import LanguageFrame, build_language_frame
from .learning.multilanguage import MultiLanguageCodeInterpreter


@dataclass(frozen=True)
class LogicAdapterResult:
    model: LogicModel
    representation: str
    source: str


class TextLogicAdapter:
    """Project semantic language frames into relational logic."""

    def adapt(self, text_or_frame: str | LanguageFrame, *, source_id: str = "text") -> LogicAdapterResult:
        frame = text_or_frame if isinstance(text_or_frame, LanguageFrame) else build_language_frame(text_or_frame)
        nodes: list[LogicNode] = []
        node_ids: dict[str, str] = {}
        for index, entity in enumerate(frame.entities):
            node_id = f"entity:{index}"
            node_ids.setdefault(entity.text.lower(), node_id)
            nodes.append(LogicNode(node_id, "entity", entity.kind, entity.text))
        for index, event in enumerate(frame.events):
            node_id = f"event:{index}"
            nodes.append(LogicNode(node_id, "event", "causal", event.predicate,
                                   (("modality", event.modality), ("confidence", event.confidence))))
        relations: list[LogicRelation] = []
        for relation in frame.relations:
            subject = node_ids.get(relation.subject.lower())
            obj = node_ids.get((relation.object or "").lower())
            if subject and obj:
                relations.append(LogicRelation(subject, relation.predicate, obj,
                                                (("kind", relation.kind), ("polarity", relation.polarity))))
        invariants = tuple(p.text for p in frame.semantic_propositions if p.confidence in {"high", "candidate"})
        purpose = "explain causal/relation structure" if frame.causal_relations else "represent semantic relations"
        model = model_from_parts(purpose=purpose, nodes=nodes, relations=relations,
                                 invariants=invariants, assumptions=frame.modality,
                                 source_artifacts=(source_id,), source_representations=("text",),
                                 interpretation="semantic language frame projected into role/relation structure")
        return LogicAdapterResult(model, "text", frame.text)


class CodeLogicAdapter:
    """Project Python/JavaScript/SQL computational structure into logic roles."""

    def __init__(self, interpreter: MultiLanguageCodeInterpreter | None = None) -> None:
        self.interpreter = interpreter or MultiLanguageCodeInterpreter()

    def adapt(self, source: str, *, language: str, source_id: str = "code") -> LogicAdapterResult:
        representation = self.interpreter.interpret(source, language=language)
        nodes = [LogicNode(f"step:{i}", "operation", "operation", value) for i, value in enumerate(representation.operations)]
        nodes.extend(LogicNode(f"control:{i}", "control", "control", value) for i, value in enumerate(representation.control_flow))
        nodes.extend(LogicNode(f"data:{i}", "state", "data", value) for i, value in enumerate(representation.data_flow))
        relations: list[LogicRelation] = []
        operation_nodes = [n.id for n in nodes if n.role == "operation"]
        for left, right in zip(operation_nodes, operation_nodes[1:]):
            relations.append(LogicRelation(left, "precedes", right))
        for control in [n for n in nodes if n.role == "control"]:
            for operation in operation_nodes:
                relations.append(LogicRelation(control.id, "constrains", operation))
        invariants = tuple(dict.fromkeys((
            *representation.data_flow,
            *(f"control:{item}" for item in representation.control_flow),
            f"algorithm-family:{representation.algorithm_family}",
            "executable outcome structure must be preserved",
        )))
        model = model_from_parts(purpose=representation.algorithm_family,
                                 nodes=nodes, relations=relations, invariants=invariants,
                                 source_artifacts=(source_id,), source_representations=(language,),
                                 interpretation="computational representation projected into operation/control/state roles")
        return LogicAdapterResult(model, language, source)


class MathLogicAdapter:
    """Small, auditable mathematical adapter; it preserves equations as constraints."""

    _REL = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*(<=|>=|=|<|>)\s*(.+)")

    def adapt(self, expression: str, *, source_id: str = "math") -> LogicAdapterResult:
        normalized = " ".join(expression.split())
        nodes: list[LogicNode] = []
        relations: list[LogicRelation] = []
        constraints: list[str] = []
        for index, match in enumerate(self._REL.finditer(normalized)):
            left, operator, right = match.groups()
            left_id = f"quantity:{index}:left"
            right_id = f"quantity:{index}:right"
            nodes.extend((LogicNode(left_id, "quantity", "symbol", left),
                          LogicNode(right_id, "quantity", "expression", right)))
            relations.append(LogicRelation(left_id, operator, right_id))
            constraints.append(f"{left} {operator} {right}")
        if not nodes:
            symbols = re.findall(r"[A-Za-z][A-Za-z0-9_]*", normalized)
            nodes = [LogicNode(f"symbol:{i}", "quantity", "symbol", value) for i, value in enumerate(dict.fromkeys(symbols))]
        model = model_from_parts(purpose="mathematical constraint/relation", nodes=nodes, relations=relations,
                                 constraints=constraints or (normalized,), source_artifacts=(source_id,),
                                 source_representations=("math",), interpretation="equation/constraint structure")
        return LogicAdapterResult(model, "math", expression)


class UniversalLogicAdapter:
    """Single entry point for representation-neutral extraction."""

    def __init__(self) -> None:
        self.text = TextLogicAdapter()
        self.code = CodeLogicAdapter()
        self.math = MathLogicAdapter()

    def adapt(self, artifact: Any, *, representation: str, source_id: str = "artifact", language: str | None = None) -> LogicAdapterResult:
        kind = representation.lower()
        if kind == "text":
            return self.text.adapt(artifact, source_id=source_id)
        if kind == "code":
            if not language:
                raise ValueError("language is required for code artifacts")
            return self.code.adapt(artifact, language=language, source_id=source_id)
        if kind == "math":
            return self.math.adapt(artifact, source_id=source_id)
        raise ValueError(f"unsupported representation: {representation}")
