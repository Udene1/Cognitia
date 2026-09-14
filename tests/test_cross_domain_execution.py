"""Tests for the first executable cross-domain transfer milestone."""
from cognitia.cross_domain_execution import CrossDomainExecutionPipeline, LogicExecutionCompiler
from cognitia.text_rule_logic import TextRuleLogicAdapter
from cognitia.logic_ir import LogicNode, LogicRelation, model_from_parts


def test_text_reasoning_transfers_to_an_economics_target_and_executes():
    source = TextRuleLogicAdapter().adapt("demand > capacity", source_id="source:text-rule")
    target = TextRuleLogicAdapter().adapt("revenue > cost", source_id="target:economics-problem")

    result = CrossDomainExecutionPipeline().execute_and_verify(
        source, target, {"revenue": 120, "cost": 80}
    )

    assert result.execution.value is True
    assert result.verification.passed
    assert result.candidate.structural_score > 0
    assert source.provenance is not None
    assert source.provenance.source_artifacts == ("source:text-rule",)


def test_failed_target_observation_rejects_transfer():
    source = TextRuleLogicAdapter().adapt("demand > capacity", source_id="source")
    target = TextRuleLogicAdapter().adapt("revenue > cost", source_id="target")

    result = CrossDomainExecutionPipeline().execute_and_verify(
        source, target, {"revenue": 70, "cost": 80}
    )

    assert result.execution.value is False
    assert not result.verification.passed


def test_execution_program_retains_source_fingerprint():
    model = model_from_parts(
        purpose="arithmetic",
        nodes=(LogicNode("a", "quantity", "symbol", "a"), LogicNode("b", "quantity", "symbol", "b")),
        relations=(LogicRelation("a", ">", "b"),),
        source_artifacts=("source",),
    )
    program = LogicExecutionCompiler().compile(model)
    assert program.source_fingerprint == model.fingerprint()
