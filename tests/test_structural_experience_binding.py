from cognitia.structural_experience import signature, structural_signature_matches


TRAIN = "The database outage caused the payment queue to stall. The database outage reduced worker throughput."
HELD_OUT = "The mirror coating change caused the telescope image to degrade. The mirror coating change reduced optical throughput."
BINDING_REVERSED = "The mirror coating change caused the telescope image to degrade. The optical throughput reduced the mirror coating change."


def test_binding_pattern_transfers_across_lexically_different_domains():
    assert structural_signature_matches(signature(TRAIN), signature(HELD_OUT))


def test_binding_pattern_rejects_rewired_arguments():
    assert not structural_signature_matches(signature(TRAIN), signature(BINDING_REVERSED))
