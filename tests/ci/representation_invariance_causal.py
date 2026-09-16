"""Evaluate candidate causal representation across equivalent surface forms."""
from __future__ import annotations

import json
from pathlib import Path

from cognitia.language.representation import build_language_frame

VARIANTS = (
    ("why_after", "Why did the payment queue stall after the database outage?"),
    ("explicit", "The database outage caused the payment queue to stall."),
    ("because", "The payment queue stalled because the database outage occurred."),
    ("what_caused", "What caused the payment queue to stop?"),
)


def main() -> None:
    records = []
    for name, text in VARIANTS:
        frame = build_language_frame(text)
        records.append({
            "name": name,
            "text": text,
            "causal_relations": [
                {
                    "predicate": relation.predicate,
                    "kind": relation.kind,
                    "confidence": relation.confidence,
                    "subject": relation.subject,
                    "object": relation.object,
                }
                for relation in frame.causal_relations
            ],
            "shape": [(relation.kind, relation.predicate) for relation in frame.causal_relations],
        })

    shapes = [tuple(item["shape"]) for item in records]
    artifact = {
        "experiment": "representation-invariance-causal-v1",
        "research_question": "Do equivalent causal surface forms converge on the same candidate relation family before abstraction induction?",
        "protocol": {
            "equivalence_classes": "researcher-defined controlled linguistic variants",
            "truth_claim": "none; relations remain candidate interpretations",
        },
        "records": records,
        "observations": {
            "all_emit_causal_relation": all(record["causal_relations"] for record in records),
            "all_use_causal_predicate": all(any(item["predicate"] == "caused" for item in record["causal_relations"]) for record in records),
            "same_relation_shape": len(set(shapes)) == 1,
            "candidate_confidence_preserved": all(
                all(item["confidence"] == "candidate" for item in record["causal_relations"])
                for record in records
            ),
        },
        "interpretation_boundary": "Convergence of candidate representations is a representation-invariance result only; it does not establish that the inferred causal relation is true.",
    }
    output = Path(".ci/representation-invariance-causal.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
