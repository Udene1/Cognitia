import pytest

from cognitia.learning.behavioral_verification import verify_equivalent


def test_matching_implementations_are_verified_on_held_out_cases():
    left = lambda rows: {k: sum(v for key, v in rows if key == k) for k in {key for key, _ in rows}}
    right = lambda rows: _imperative(rows)
    cases = [
        [("Ada", 2), ("Bola", 3), ("Ada", 5)],
        [("Chidi", 7)],
        [],
    ]
    # Empty input is included as a held-out edge case; both implementations agree.
    result = verify_equivalent(left, right, cases)
    assert result.verified
    assert result.cases_checked == 3
    assert result.mismatches == ()


def test_behavioral_mismatch_blocks_equivalence():
    result = verify_equivalent(lambda value: value + 1, lambda value: value + 2, [1, 2, 3])
    assert not result.verified
    assert result.cases_checked == 3
    assert len(result.mismatches) == 3


def test_empty_verification_set_is_not_evidence():
    with pytest.raises(ValueError):
        verify_equivalent(lambda value: value, lambda value: value, [])


def _imperative(rows):
    totals = {}
    for key, value in rows:
        totals[key] = totals.get(key, 0) + value
    return totals
