"""First end-to-end discovery primitive experiment.

This is intentionally not a novel-idea generator. It tests whether Cognitia can
separate explained observations from an explanatory gap and preserve that gap as
the starting point for later hypothesis-space exploration.
"""
from cognitia.discovery import DiscoveryWorkspace, ExplanationAssessment, ExplanationStatus, Observation

workspace = DiscoveryWorkspace()
workspace.add_observation(Observation("o1", "model predicts stable output under condition A"))
workspace.add_observation(Observation("o2", "measured output increases under condition A", source="experiment-1"))
workspace.assess(ExplanationAssessment("o1", ExplanationStatus.EXPLAINED, "baseline model statement"))
workspace.assess(ExplanationAssessment("o2", ExplanationStatus.CONTRADICTED, "current model predicts no increase"))

gaps = workspace.identify_gaps()
assert len(gaps) == 1
assert gaps[0].observation_ids == ("o2",)
assert gaps[0].missing_aspects == ("current model predicts no increase",)

print("DISCOVERY_GAP_IDENTIFIED")
print(f"OBSERVATION: {gaps[0].observation_ids[0]}")
print(f"MISSING_ASPECT: {gaps[0].missing_aspects[0]}")
print("NO_HYPOTHESIS_GENERATED: True")
