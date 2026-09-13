# Cognitia Milestones

## 2026-09-13 — Evidence reasoning capability proof

### Goal
Move evidence reasoning from primitive/unit-level verification to a capability-level problem-solving test, analogous to the earlier executable-code capability proofs.

### Built
- Added `cognitia/benchmarks/evidence_reasoning.py`.
- Added deterministic adversarial problem cases covering:
  - correlated/copied source slop;
  - independent contradiction;
  - stale evidence;
  - model conflict;
  - insufficient evidence.
- Added an executable solver trace that records whether Cognitia actually used:
  - provenance-aware independence grouping;
  - contradiction detection;
  - stale-evidence detection;
  - model checking;
  - next-test selection.
- Added a naive source-count trace so evidence-aware reasoning can be compared against raw source counting.
- Added `tests/ci/evidence_reasoning_problem.py` as an end-to-end CI capability proof.
- Added the capability benchmark to `.github/workflows/test.yml`.
- Hardened `EvidenceConvergenceEngine` so supporting and contradicting evidence cannot borrow reliability from the opposite polarity through a shared provenance root.

### Capability standard
The benchmark does **not** merely assert that an evidence class returns the expected object. It gives Cognitia a problem containing misleading, duplicated, stale, contradictory, and incomplete evidence and evaluates the resulting reasoning trace and conclusion.

A correct result may be `unresolved`; overconfidence is treated as failure when the evidence is insufficient.

### Verified CI result
GitHub Actions run **#297** (`34747256544`) completed successfully on commit `5affee5c0a8343e95da6b86ecbfa67768e311fa5`.

The capability benchmark produced:

| Problem | Naive evidence | Independent evidence | Stale | Model check | Conclusion |
|---|---:|---:|---|---|---|
| Correlated source slop | 6 support / 1 contradiction | 1 support / 1 contradiction | none | not needed | **contradicted** |
| Independent conflict | 1 support / 1 contradiction | 1 / 1 | none | not needed | **conflicted** |
| Stale data | 1 support / 1 contradiction | 1 / 1 | `old` detected | not needed | **conflicted** |
| Model check | 1 support / 0 contradiction | 1 / 0 | none | `model_conflict` | **supported, with model conflict** |
| Insufficient evidence | 0 / 0 | 0 / 0 | none | not needed | **unresolved** |

**Benchmark: 5/5 passed.** `CAPABILITY_TRACE_VALIDATED` was emitted by CI.

The run also verified the surrounding research stack in the same job: unit tests passed, parallel multi-environment investigation passed, evidence convergence/model checks passed, and validated-knowledge persistence passed.

### What the benchmark exposed
The first execution caught a real defect in the evidence convergence weighting: shared provenance could cause a source's reliability to influence both supporting and contradicting sides. The adversarial benchmark exposed this because six copied sources plus one primary contradiction incorrectly produced a conflict instead of a contradiction. The convergence implementation was corrected so weighting is polarity-specific. The next CI execution then produced the expected `contradicted` result and passed all five cases.

This is exactly the standard we want: the benchmark is allowed to find flaws in Cognitia rather than being written only to demonstrate success.

### Research significance
This establishes the next testing layer for Cognitia:

`primitive → subsystem → capability → real problem-solving behavior`

The target is not to prove that Cognitia has "good search". The target is to prove that it can reason over an adversarial evidence landscape, avoid counting copied information as independent confirmation, recognize contradiction and stale observations, use relevant models as constraints, choose a useful next test, and remain epistemically calibrated when the evidence does not justify a conclusion.

### Next bar
The current benchmark is deterministic and synthetic. The next escalation is to connect the same capability trace to real environment adapters and multi-environment evidence, then test whether Cognitia can construct and update an evidence landscape from genuinely external observations without an LLM dependency.
