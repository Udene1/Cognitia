# Cognitia Milestones

## 2026-09-13/14 — Evidence reasoning → experiment-driven problem solving

### Evidence reasoning capability proof

Moved evidence reasoning from primitive/unit-level verification to capability-level problem solving.

Built:
- provenance-aware evidence convergence;
- correlated/copied-source detection;
- independent contradiction preservation;
- stale-evidence detection;
- model-consistency checks;
- calibrated `unresolved` outcomes;
- next-test selection;
- executable CI capability benchmark with five adversarial problems.

### Verified result

GitHub Actions run **#297** (`34747256544`) completed successfully on commit `5affee5c0a8343e95da6b86ecbfa67768e311fa5`.

The benchmark recorded:

| Problem | Naive evidence | Independent evidence | Special result | Conclusion |
|---|---:|---:|---|---|
| Correlated source slop | 6 support / 1 contradiction | 1 support / 1 contradiction | copied lineage collapsed | **contradicted** |
| Independent conflict | 1 / 1 | 1 / 1 | contradiction preserved | **conflicted** |
| Stale data | 1 / 1 | 1 / 1 | `old` detected stale | **conflicted** |
| Model check | 1 / 0 | 1 / 0 | `model_conflict` surfaced | **supported with model conflict** |
| Insufficient evidence | 0 / 0 | 0 / 0 | independent test requested | **unresolved** |

**Benchmark: 5/5 passed.** The first execution exposed a real polarity-weighting defect; the convergence implementation was hardened so a shared provenance root cannot lend reliability to the opposite evidence polarity. The corrected run passed.

This establishes the testing ladder:

`primitive → subsystem → capability → real problem-solving behavior`

## 2026-09-14 — Discriminating experiment capability

### Goal

Push beyond recognizing an evidence problem. Cognitia must choose an action that can distinguish competing explanations, execute/observe the test in an environment, and use the result to update the surviving hypothesis.

### Built

- Added `cognitia/benchmarks/decision_experiment.py`.
- Added an executable decision problem with two competing causal explanations and an irrelevant third prediction under a different condition.
- Cognitia selects the discriminating experiment rather than the irrelevant prediction.
- The selected experiment has positive expected information gain.
- A simulated observation is applied to the selected predictions.
- The solver identifies the surviving hypothesis and rejected hypothesis from the observation.
- Added `tests/ci/decision_experiment_problem.py`.
- Added the capability proof to `.github/workflows/test.yml`.

### Deterministic capability target

Problem: explain a latency anomaly.

- Hypothesis A predicts latency remains high when the cache is isolated.
- Hypothesis B predicts latency falls under the same condition.
- An unrelated hypothesis has a prediction under a different condition and must not be treated as discriminating.
- Observation: `latency falls`.

Expected behavior:

`competing hypotheses → discriminating experiment → observation → hypothesis update`

The expected selected experiment is `experiment:cache:p1:network:p1`, with information gain `1.0`, leaving `network-failure` as the survivor.

### Verification status

**Implementation complete; CI execution is pending for the new commit.** No CI-green claim is made until GitHub Actions actually executes this new benchmark.

## Next research bar

The next step is to connect experiment selection to the evidence landscape and parallel environments:

`problem → hypotheses → predictions → choose highest-value test → execute in environment → observe → update evidence → revise hypotheses`

After that, replace synthetic observations with real environment adapters. The benchmark should eventually measure whether Cognitia can solve novel problems using independently gathered observations, not merely pass hand-authored scenarios.
