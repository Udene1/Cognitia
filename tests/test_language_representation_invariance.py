from cognitia.language.representation import build_language_frame


VARIANTS = (
    "Why did the payment queue stall after the database outage?",
    "The database outage caused the payment queue to stall.",
    "The payment queue stalled because the database outage occurred.",
    "What caused the payment queue to stop?",
)


NOVEL_VARIANTS = (
    "Why did the telescope image degrade after the mirror coating changed?",
    "Why did the database outage cause the payment queue to stall?",
)


def test_equivalent_causal_surface_forms_emit_candidate_causal_relations():
    frames = [build_language_frame(text) for text in VARIANTS]
    assert all(frame.causal_relations for frame in frames)
    assert all(relation.kind == "causal" for frame in frames for relation in frame.causal_relations)
    assert all(relation.predicate == "caused" for frame in frames for relation in frame.causal_relations)


def test_unseen_causal_question_forms_emit_candidate_causal_relations():
    frames = [build_language_frame(text) for text in NOVEL_VARIANTS]
    assert all(frame.causal_relations for frame in frames)
    assert all(relation.kind == "causal" for frame in frames for relation in frame.causal_relations)
    assert all(relation.predicate == "caused" for frame in frames for relation in frame.causal_relations)
