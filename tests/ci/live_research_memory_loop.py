"""Prove live research -> validation -> durable memory -> later retrieval.

The parent process deliberately runs Cognitia twice in fresh Python subprocesses.
The first process researches and promotes only independently corroborated factors.
The second process receives the same question after the first process has exited and
must retrieve those durable propositions before choosing its fresh searches.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from cognitia.durable import SQLiteCognitiveJournal
from cognitia.knowledge.validated import ValidatedKnowledgeStore

QUESTION = "Why did the Roman Empire decline, and what evidence distinguishes the competing explanations?"


def _child(stage: str, db_path: Path) -> dict:
    env = dict(os.environ)
    env["COGNITIA_MEMORY_STAGE"] = stage
    env["COGNITIA_MEMORY_DB"] = str(db_path)
    completed = subprocess.run(
        [sys.executable, __file__],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    print(completed.stdout, end="")
    return json.loads(completed.stdout.strip().splitlines()[-1])


def _run_stage(stage: str, db_path: Path) -> None:
    with SQLiteCognitiveJournal(db_path) as journal:
        store = ValidatedKnowledgeStore(journal)
        if stage == "write":
            from cognitia.open_research import OpenEndedResearch

            result, synthesis = OpenEndedResearch(knowledge_store=store).investigate_and_synthesize(
                QUESTION,
                max_rounds=4,
                search_results=8,
                documents_per_round=5,
                claims_per_document=20,
            )
            factor_evidence = [
                {"factor": factor.factor, "origins": factor.origin_count, "confidence": factor.confidence}
                for factor in synthesis.factors
            ]
            payload = {
                "stage": stage,
                "prior_knowledge": len(result.prior_knowledge),
                "promoted_knowledge": len(result.promoted_knowledge),
                "durable_count": len(store.recover()),
                "factors": len(synthesis.factors),
                "factor_evidence": factor_evidence,
            }
            print("LIVE_RESEARCH_MEMORY_WRITE", flush=True)
            print(json.dumps(payload), flush=True)
            return

        if stage == "read":
            from cognitia.open_research import OpenEndedResearch

            recovered_before = store.recover()
            result = OpenEndedResearch(knowledge_store=store).investigate(
                QUESTION,
                max_rounds=4,
                search_results=8,
                documents_per_round=5,
                claims_per_document=20,
            )
            memory_actions = [
                research_round.decision_rationale
                for research_round in result.rounds
                if "informed by durable knowledge" in research_round.decision_rationale
            ]
            payload = {
                "stage": stage,
                "recovered_before_research": len(recovered_before),
                "prior_knowledge": len(result.prior_knowledge),
                "memory_informed_rounds": len(memory_actions),
                "memory_ids": [item.id for item in result.prior_knowledge],
                "first_query": result.rounds[0].action.query.objective if result.rounds else "",
            }
            print("LIVE_RESEARCH_MEMORY_READ", flush=True)
            print(json.dumps(payload), flush=True)
            if not recovered_before:
                raise AssertionError("fresh process recovered no durable knowledge")
            if not result.prior_knowledge:
                raise AssertionError("live research did not retrieve durable knowledge")
            if not memory_actions:
                raise AssertionError("retrieved memory did not influence research actions")
            return

        raise ValueError(stage)


def main() -> None:
    stage = os.environ.get("COGNITIA_MEMORY_STAGE")
    db = os.environ.get("COGNITIA_MEMORY_DB")
    if stage:
        _run_stage(stage, Path(db))
        return

    with tempfile.TemporaryDirectory(prefix="cognitia-memory-loop-") as directory:
        db_path = Path(directory) / "cognition.sqlite"
        write = _child("write", db_path)
        if write["promoted_knowledge"] < 1:
            raise AssertionError(f"live research promoted no durable knowledge: {write}")
        read = _child("read", db_path)
        if read["recovered_before_research"] != write["durable_count"]:
            raise AssertionError(f"durable count changed across restart: write={write} read={read}")
        print("LIVE_RESEARCH_MEMORY_LOOP_SUCCESS")


if __name__ == "__main__":
    main()
