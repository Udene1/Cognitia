from cognitia.benchmarks.evidence_reasoning import EvidenceReasoningBenchmark, format_results

results = EvidenceReasoningBenchmark().run()
print(format_results(results))
assert all(result.passed for result in results)
assert any(
    result.trace.naive_support_count > result.trace.independent_support_groups
    for result in results
)
assert any(result.trace.status == "unresolved" for result in results)
assert any(result.trace.model_checked and result.trace.model_status == "model_conflict" for result in results)
print("CAPABILITY_TRACE_VALIDATED")
