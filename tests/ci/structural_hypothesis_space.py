"""CI research experiment: expand an explanatory model structurally."""
from cognitia.discovery_structure import (
    ModelElement,
    ModelRelation,
    RelationKind,
    StructuralHypothesisBuilder,
    StructuralModel,
)

model = StructuralModel(
    id="baseline-engine",
    elements=(
        ModelElement("input", "variable", "input"),
        ModelElement("load", "variable", "load"),
        ModelElement("output", "variable", "output"),
    ),
    relations=(ModelRelation("load", RelationKind.CAUSES, "output"),),
)

alternatives = StructuralHypothesisBuilder().build(model)
assert alternatives
assert any(item.operation == "reverse_relation" for item in alternatives)
assert any(item.operation == "add_dependency" for item in alternatives)
assert all(item.epistemic_status == "hypothesis" for item in alternatives)
assert all(item.novelty_status == "unassessed" for item in alternatives)

print("STRUCTURAL_HYPOTHESIS_SPACE_CONSTRUCTED")
print(f"STRUCTURAL_ALTERNATIVES: {len(alternatives)}")
print("NOVELTY_CLAIM: NONE")
print("STRUCTURAL_SEARCH_SUCCESS")
