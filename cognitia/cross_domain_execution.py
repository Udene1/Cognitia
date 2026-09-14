"""A small executable target for verified cross-domain logic transfer.

This is intentionally a constrained first compiler, not a claim of general
program synthesis. It executes relation-level arithmetic/constraints emitted
by the common logic substrate and records every target observation used for
verification.
"""
from __future__ import annotations

from dataclasses import dataclass
import operator
from typing import Mapping

from .logic_ir import LogicModel, LogicTransferCandidate, LogicTransferEngine, LogicTransferVerification


@dataclass(frozen=True)
class ExecutableInstruction:
    operator: str
    output: str
    operands: tuple[str, ...]


@dataclass(frozen=True)
class ExecutableLogic:
    instructions: tuple[ExecutableInstruction, ...]
    output: str
    source_fingerprint: str


@dataclass(frozen=True)
class ExecutionResult:
    value: object
    state: tuple[tuple[str, object], ...]
    observations: tuple[Mapping[str, object], ...]


class LogicExecutionCompiler:
    """Compile a constrained LogicModel into an auditable executable form."""

    _OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}

    def compile(self, model: LogicModel) -> ExecutableLogic:
        instructions: list[ExecutableInstruction] = []
        for relation in model.relations:
            source = model.node(relation.source).value or relation.source
            target = model.node(relation.target).value or relation.target
            if relation.relation in self._OPS:
                instructions.append(ExecutableInstruction(relation.relation, target, (source,)))
            elif relation.relation in {"=", ">", ">=", "<", "<="}:
                instructions.append(ExecutableInstruction("compare:" + relation.relation, target, (source,)))
        if not instructions:
            raise ValueError("logic model has no executable relation")
        return ExecutableLogic(tuple(instructions), instructions[-1].output, model.fingerprint())

    def run(self, program: ExecutableLogic, inputs: Mapping[str, object]) -> ExecutionResult:
        state: dict[str, object] = dict(inputs)
        observations: list[Mapping[str, object]] = []
        for instruction in program.instructions:
            if not instruction.operands:
                raise ValueError("instruction has no operands")
            left = state[instruction.operands[0]]
            if instruction.operator.startswith("compare:"):
                symbol = instruction.operator.split(":", 1)[1]
                right = state[instruction.output]
                verdict = {"=": operator.eq, ">": operator.gt, ">=": operator.ge,
                           "<": operator.lt, "<=": operator.le}[symbol](left, right)
                state[instruction.output] = verdict
                observations.append({"verified": bool(verdict), "description": f"{left} {symbol} {right}"})
                continue
            fn = self._OPS[instruction.operator]
            right = state[instruction.output]
            state[instruction.output] = fn(left, right)
            observations.append({"verified": True, "description": f"{left} {instruction.operator} {right} -> {state[instruction.output]}"})
        return ExecutionResult(state[program.output], tuple(state.items()), tuple(observations))


@dataclass(frozen=True)
class CrossDomainExecutionResult:
    candidate: LogicTransferCandidate
    execution: ExecutionResult
    verification: LogicTransferVerification


class CrossDomainExecutionPipeline:
    """Compare transferred logic, execute the target, then verify observations."""

    def __init__(self) -> None:
        self.compiler = LogicExecutionCompiler()
        self.transfer = LogicTransferEngine()

    def execute_and_verify(
        self,
        source: LogicModel,
        target: LogicModel,
        inputs: Mapping[str, object],
    ) -> CrossDomainExecutionResult:
        candidate = self.transfer.compare(source, target)
        program = self.compiler.compile(target)
        execution = self.compiler.run(program, inputs)
        verification = self.transfer.verify(candidate, execution.observations)
        return CrossDomainExecutionResult(candidate, execution, verification)
