"""Cognitia: experimental artificial cognitive system."""

from .acquisition import (
    AcquisitionProposal,
    AcquisitionStage,
    CapabilityRequirement,
    propose_capability_acquisition,
)

__version__ = "0.1.0"

__all__ = [
    "AcquisitionProposal",
    "AcquisitionStage",
    "CapabilityRequirement",
    "propose_capability_acquisition",
    "__version__",
]
