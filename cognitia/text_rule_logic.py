"""Small auditable bridge from plain conditional text into Logic IR.

This parser intentionally supports a narrow, explicit rule form. Its purpose is
to prove the end-to-end architecture without pretending that arbitrary language
has been compiled into executable semantics.
"""
from __future__ import annotations

import re

from .logic_ir import LogicNode, LogicRelation, LogicModel, model_from_parts


class TextRuleLogicAdapter:
    _PATTERN = re.compile(
        r"^\s*(?P<left>[A-Za-z][A-Za-z0-9_]*)\s+(?P<relation>>=|<=|>|<|=)\s+(?P<right>[A-Za-z][A-Za-z0-9_]*)\s*$",
    )

    def adapt(self, text: str, *, source_id: str = "text-rule") -> LogicModel:
        match = self._PATTERN.match(text)
        if not match:
            raise ValueError("supported text rule must be: <quantity> <relation> <quantity>")
        left, relation, right = match.group("left"), match.group("relation"), match.group("right")
        nodes = (
            LogicNode("left", "quantity", "symbol", left),
            LogicNode("right", "quantity", "symbol", right),
        )
        return model_from_parts(
            purpose="conditional quantitative comparison",
            nodes=nodes,
            relations=(LogicRelation("left", relation, "right"),),
            constraints=(text,),
            invariants=("preserve the comparison relation between the two quantities",),
            source_artifacts=(source_id,),
            source_representations=("text",),
            interpretation="explicit quantitative relation extracted from text",
        )
