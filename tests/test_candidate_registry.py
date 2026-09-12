import pytest

from cognitia.capability_acquisition import CapabilityCandidate, AcquisitionMode
from cognitia.candidate_registry import CandidateRecord, CandidateRegistry, CandidateState


def candidate():
    return CapabilityCandidate("reasoning", AcquisitionMode.COMPOSE, ("op",), lambda x: x, "identity")


def test_candidate_survives_hold_and_can_later_verify():
    registry = CandidateRegistry([CandidateRecord("c1", candidate())])
    registry.benchmark("c1", 0.9)
    registry.hold("c1", "protected capability regressed")
    assert registry.get("c1").state is CandidateState.HELD
    registry.verify("c1")
    assert registry.promote("c1").state is CandidateState.PROMOTED


def test_unverified_candidate_cannot_promote():
    registry = CandidateRegistry([CandidateRecord("c1", candidate())])
    with pytest.raises(ValueError, match="only verified"):
        registry.promote("c1")


def test_duplicate_candidates_are_not_silently_replaced():
    registry = CandidateRegistry([CandidateRecord("c1", candidate())])
    with pytest.raises(ValueError, match="already exists"):
        registry.add(CandidateRecord("c1", candidate()))
