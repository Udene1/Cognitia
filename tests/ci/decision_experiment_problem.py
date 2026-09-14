from cognitia.benchmarks.decision_experiment import DecisionExperimentBenchmark, format_results

results = DecisionExperimentBenchmark().run()
print(format_results(results))
assert results
assert all(passed for _, _, passed in results)
assert any(trace.expected_information_gain > 0 for _, trace, _ in results)
assert any(trace.surviving_hypothesis is not None for _, trace, _ in results)
print("DISCRIMINATING_EXPERIMENT_CAPABILITY_PROOF_SUCCESS")
