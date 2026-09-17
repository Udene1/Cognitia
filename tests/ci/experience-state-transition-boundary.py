"""Audit whether recorded experience state updates reach active cognition.

This is intentionally a boundary audit, not a new state-update mechanism. The
previous candidate-generation experiment showed that retrieved experience does
not enter StateActionGenerator directly. The next question is whether the
existing ``Experience.state_update`` field is consumed anywhere that can feed a
subsequent CognitiveState into cognition.

The experiment therefore traces the repository's source-level references to
``state_update`` and records the actual consumers. It must not manufacture a
transition merely to make the experiment positive.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ARTIFACT = Path(".ci/experience-state-transition-boundary.json")
ROOT = Path("cognitia")


def python_files() -> list[Path]:
    return sorted(ROOT.rglob("*.py"))


def references() -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in python_files():
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "state_update":
                hits.append({"path": str(path), "line": node.lineno, "kind": "name"})
            elif isinstance(node, ast.Attribute) and node.attr == "state_update":
                hits.append({"path": str(path), "line": node.lineno, "kind": "attribute"})
    return hits


def main() -> None:
    hits = references()
    experience_definition = [
        item for item in hits
        if item["path"] == "cognitia/experience.py"
    ]
    external_consumers = [
        item for item in hits
        if item["path"] != "cognitia/experience.py"
    ]

    record = {
        "experiment": "experience-state-transition-boundary",
        "research_question": "Does recorded Experience.state_update currently reach active cognition as a state transition?",
        "method": "AST audit of all Python source under cognitia/ for references to state_update; no transition mechanism is introduced by the experiment.",
        "references": hits,
        "experience_definition_references": experience_definition,
        "external_consumers": external_consumers,
        "external_consumer_count": len(external_consumers),
        "state_update_is_recorded": bool(experience_definition),
        "state_update_has_external_consumer": bool(external_consumers),
        "interpretation": (
            "The repository records Experience.state_update as part of an auditable experience, "
            "but no external Cognitia module currently consumes that field. Therefore the current "
            "architecture has no implemented experience-derived state transition feeding subsequent cognition. "
            "This is an architectural boundary observation, not evidence that experience-derived state updates "
            "cannot be useful or cannot be implemented later."
            if not external_consumers
            else
            "Experience.state_update has external consumers. Those consumers must be inspected before concluding "
            "that experience is isolated from subsequent cognitive state."
        ),
        "research_constraint": "Do not add a state-transition mechanism inside this experiment; first characterize the boundary that actually exists.",
        "next_boundary": "If a state transition is introduced, test it as a separate capability with explicit provenance, competing evidence, refutation, and regression checks rather than assuming state_update is authoritative.",
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
