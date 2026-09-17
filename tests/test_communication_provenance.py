from cognitia.communication_provenance import (
    CapabilityOrigin,
    CapabilityProvenance,
    CommunicationProvenanceRegistry,
)


def test_engineered_capability_is_not_labelled_as_learned() -> None:
    record = CapabilityProvenance(
        capability="recipient-sensitive communication",
        origin=CapabilityOrigin.DEVELOPER_SPECIFIED,
        introduced_by="PR #9",
        evidence=("PR #9",),
        validated_by=("PR #12",),
        later_boundaries=("PR #47",),
        current_status="engineered mechanism; not independently learned",
        independent_of_handholding=False,
    )

    assert record.learned_claim_supported is False
    assert record.as_dict()["origin"] == "developer_specified"
    assert record.as_dict()["later_boundaries"] == ["PR #47"]


def test_experience_derived_claim_requires_independence_and_validation() -> None:
    record = CapabilityProvenance(
        capability="communication adaptation",
        origin=CapabilityOrigin.EXPERIENCE_DERIVED,
        introduced_by="future experiment",
        validated_by=("future held-out transfer",),
        independent_of_handholding=True,
        current_status="candidate learned capability",
    )

    assert record.learned_claim_supported is True


def test_registry_rejects_duplicate_capability_claims() -> None:
    record = CapabilityProvenance(
        capability="representation-preserving communication",
        origin=CapabilityOrigin.DEVELOPER_SPECIFIED,
        introduced_by="PR #10",
        current_status="engineered mechanism",
    )
    registry = CommunicationProvenanceRegistry.from_iterable((record,))

    assert registry.get(record.capability) == record

    try:
        registry.add(record)
    except ValueError as exc:
        assert "duplicate capability provenance" in str(exc)
    else:
        raise AssertionError("duplicate capability provenance was accepted")
