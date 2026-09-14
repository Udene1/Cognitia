from cognitia.benchmarks.investigation_loop import benchmark, format_result

trace = benchmark()
print(format_result(trace))
assert trace.environments == ("web", "experiment", "simulation")
assert trace.evidence_count == 5
assert trace.initial_status == "contradicted"
assert trace.independent_support_groups == 2
assert trace.independent_contradiction_groups == 1
assert trace.selected_experiment == "experiment:cache:p1:network:p1"
assert trace.selected_information_gain > 0
assert trace.experiment_observation == "claim confirmed"
assert trace.updated_status == "conflicted"
assert trace.capability_used
print("INTEGRATED_INVESTIGATION_CAPABILITY_PROOF_SUCCESS")
