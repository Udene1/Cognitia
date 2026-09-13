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

### Capability standard
The benchmark does **not** merely assert that an evidence class returns the expected object. It gives Cognitia a problem containing misleading, duplicated, stale, contradictory, and incomplete evidence and evaluates the resulting reasoning trace and conclusion.

A correct result may be `unresolved`; overconfidence is treated as failure when the evidence is insufficient.

### CI verification
The benchmark was added in commit `90f12789564690ee4edb7dd0f225c9c804a0e63e` and triggered GitHub Actions run **#292** (`34746925710`). The final benchmark result will be recorded here only after the run completes; an in-progress run is not counted as a pass.

### Research significance
This establishes the next testing layer for Cognitia:

`primitive → subsystem → capability → real problem-solving behavior`

The target is not to prove that Cognitia has "good search". The target is to prove that it can reason over an adversarial evidence landscape, avoid counting copied information as independent confirmation, recognize contradiction and stale observations, use relevant models as constraints, choose a useful next test, and remain epistemically calibrated when the evidence does not justify a conclusion.
