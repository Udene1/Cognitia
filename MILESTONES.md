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

### Verified result

GitHub Actions run **#305** (`34812836512`) completed successfully on the PR merge commit. The discriminating experiment benchmark passed:

- selected experiment: `experiment:cache:p1:network:p1`;
- information gain: `1.000`;
- observation: `latency falls`;
- surviving hypothesis: `network-failure`;
- rejected hypothesis: `cache-failure`;
- benchmark: **1/1 passed**;
- capability proof: `DISCRIMINATING_EXPERIMENT_CAPABILITY_PROOF_SUCCESS`.

The same run also passed the existing cognitive-transfer, persistence, discovery, parallel-investigation, evidence-convergence, evidence-reasoning, and validated-knowledge CI steps. The evidence-reasoning benchmark specifically passed **5/5** again, including the correlated-source case concluding `contradicted`.

## 2026-09-14 — Evidence → experiment integrated investigation loop

### Goal

Connect the evidence landscape to action selection instead of keeping evidence reasoning and experiment selection as separate demonstrations.

### Built

- Added `cognitia/benchmarks/investigation_loop.py`.
- Added a deterministic end-to-end environment fixture using the same `EnvironmentSource` boundary intended for future real adapters.
- Parallel acquisition now feeds environment observations into canonical `EvidenceRecord` objects.
- Evidence convergence evaluates the combined landscape before action selection.
- A discriminating experiment is selected from the competing prediction space.
- The follow-up observation is fed back into the evidence landscape and convergence is recomputed.
- Hardened `ParallelInvestigator` to respect the keyword-only `limit` boundary of `EnvironmentSource.observe`.
- Added `tests/ci/investigation_loop.py` and a dedicated CI step.

### Capability target

`problem → parallel environments → evidence landscape → convergence → discriminating experiment → observation → updated evidence`

The fixture deliberately includes three correlated web reports, one independent controlled measurement, and one simulation observation. The expected initial state is `contradicted`, with two independent support groups and one independent contradiction group; the selected follow-up experiment must have positive information gain and the updated evidence must become `conflicted` rather than silently overwriting the contradiction.

### Verification status

**Implementation complete; CI verification pending for the latest commit.** The last completed run (#305) predates this integrated-loop commit, so it is not being used as proof for this new capability.

## Next research bar

Replace deterministic environment fixtures with real adapters while preserving the same interfaces and epistemic boundaries:

`problem → hypotheses → predictions → parallel real environments → evidence graph → convergence/model checks → highest-value experiment → observation → state update → validated knowledge`

The benchmark should eventually measure whether Cognitia can construct and revise evidence landscapes from genuinely external observations and solve novel problems without an LLM.
