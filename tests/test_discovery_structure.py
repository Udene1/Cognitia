import pytest

from cognitia.discovery_structure import (
    ModelElement,
    ModelRelation,
    RelationKind,
    StructuralHypothesisBuilder,
    StructuralModel,
)


def test_structural_alternatives_change_model_structure_and_preserve_provenance() -> None:
    model = StructuralModel(
        id="m",
        elements=(
            ModelElement("input", "variable", "input"),
            ModelElement("load", "variable", "load"),
            ModelElement("output", "variable", "output"),
        ),
        relations=(ModelRelation("load", RelationKind.CAUSES, "output"),),
    )
    alternatives = StructuralHypothesisBuilder().build(model)
    assert len(alternatives) == 10
    assert all(item.source_model == "m" for item in alternatives)
    assert all(item.novelty_status == "unassessed" for item in alternatives)
    assert any(item.operation == "reverse_relation" for item in alternatives)


def test_relations_must_reference_existing_elements() -> None:
    with pytest.raises(ValueError):
        StructuralModel(
            id="bad",
            elements=(ModelElement("x", "variable", "x"),),
            relations=(ModelRelation("x", RelationKind.CAUSES, "missing"),),
        )
