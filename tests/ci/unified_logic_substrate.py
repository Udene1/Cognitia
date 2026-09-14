"""CI experiment for representation-neutral logic extraction and transfer."""
from __future__ import annotations

from cognitia.logic_adapters import UniversalLogicAdapter
from cognitia.logic_ir import LogicNode, LogicRelation, LogicTransferEngine, LogicProvenance, model_from_parts
from cognitia.learning.concept_transfer import GenericLogicExtractor
from cognitia.learning.transfer import assess_transfer
from cognitia.capability_acquisition import ReasoningTrace


def main() -> None:
    adapter = UniversalLogicAdapter()

    text = adapter.adapt(
        "A policy adopts an improvement when the benefit exceeds the cost.",
        representation="text", source_id="text:tradeoff",
    )
    code = adapter.adapt(
        "def choose(benefit, cost):\n    if benefit > cost:\n        return 'adopt'\n    return 'retain'",
        representation="code", language="python", source_id="code:tradeoff",
    )
    math = adapter.adapt("benefit > cost", representation="math", source_id="math:tradeoff")

    assert text.model.source_representations == ("text",)
    assert code.model.source_representations == ("python",)
    assert math.model.source_representations == ("math",)
    assert code.model.invariants
    assert math.model.relations

    source = model_from_parts(
        purpose="bounded adoption decision",
        nodes=(
            LogicNode("goal", "goal", "decision"),
            LogicNode("benefit", "quantity", "benefit"),
            LogicNode("cost", "quantity", "cost"),
            LogicNode("decision", "outcome", "adoption"),
        ),
        relations=(
            LogicRelation("benefit", "compared_with", "cost"),
            LogicRelation("benefit", "supports", "decision"),
            LogicRelation("cost", "constrains", "decision"),
        ),
        constraints=("benefit must exceed cost",),
        invariants=("decision remains bounded by the cost constraint",),
        source_artifacts=("experiment:source",),
        source_representations=("text",),
    )
    target = model_from_parts(
        purpose="economic investment decision",
        nodes=(
            LogicNode("goal", "goal", "investment"),
            LogicNode("return", "quantity", "expected return"),
            LogicNode("risk", "quantity", "risk"),
            LogicNode("decision", "outcome", "invest"),
        ),
        relations=(
            LogicRelation("return", "compared_with", "risk"),
            LogicRelation("return", "supports", "decision"),
            LogicRelation("risk", "constrains", "decision"),
        ),
        constraints=("expected return must justify risk",),
        source_artifacts=("experiment:target",),
        source_representations=("economics",),
    )
    candidate = LogicTransferEngine().compare(source, target)
    assert candidate.structural_score >= 0.8, candidate
    verified = LogicTransferEngine().verify(candidate, ({"verified": True, "description": "target decision obeyed the transferred relation"},))
    assert verified.passed

    provenance = LogicProvenance(("experiment:source",), interpretation="bounded decision logic")
    successful = provenance.with_transfer(target.fingerprint(), success=True)
    assert target.fingerprint() in successful.successful_transfers

    traces = (
        ReasoningTrace(context="engineering", operations=("partition", "compare", "decide"), outcome="worked"),
        ReasoningTrace(context="economics", operations=("partition", "compare", "decide"), outcome="worked"),
    )
    assessment = assess_transfer(traces, "physics")
    assert assessment.transferable
    assert assessment.context_independent
    assert "context" in assessment.reason.lower()

    extracted = GenericLogicExtractor().extract_python(
        "def choose(x, limit):\n    if x > limit:\n        return x\n    return limit",
        source_id="code:generic",
    )
    assert extracted.relations
    assert extracted.invariants

    print("UNIFIED_LOGIC_SUBSTRATE_SUCCESS")
    print("representations: text, code, math")
    print("cross_domain_relation_score:", candidate.structural_score)
    print("cross_context_transfer:", assessment.transferable)
    print("provenance_transfers:", len(successful.successful_transfers))


if __name__ == "__main__":
    main()
