# Experiment 3: Representation-Preserving Communication

## Status

**Experiment executed; preservation hypothesis failed for the tested concise representation.**

## Research question

Given one selected communicative act, can Cognitia express that act through different explicit representations without changing claims, evidence, uncertainty, epistemic status, or verification requirements?

## Controlled variables

Held constant:

- cognitive state;
- recipient;
- communicative objective;
- selected communicative act;
- claim set;
- evidence set;
- uncertainty;
- verification requirement.

Varied:

- representation: `STRUCTURED`, `CONCISE`, `EXPLANATORY`.

## Observed result — 2026-09-16

CI workflow run **35058802223** executed the experiment as part of a 197-test suite. The communication test failed on the preservation requirement for the concise representation.

The selected act was `REPORT_CURRENT_STATE`. The underlying decision contained evidence identity `E1`. The concise projection produced:

```text
act:report_current_state
claims:H1
uncertainty:no root cause is established;H1 and H2 remain discriminable candidates
verification:required
```

The payload did **not** contain `evidence:E1`.

The failure was therefore behavioral and directly relevant to the research question. It was not a syntax, build, or infrastructure failure. The preservation assertion correctly exposed that the representation surface had dropped an evidence commitment.

## Expected observation

Every projection must preserve the semantic communication contract exactly while its payload organization changes.

This experiment deliberately uses structured representations rather than asking an LLM to judge whether prose "means the same thing". That keeps semantic preservation experimentally identifiable.

## Failure interpretation

The concise projection currently violates the preservation hypothesis because it removes observable evidence identity while retaining the act, claim, uncertainty, and verification fields.

This does **not** establish that concise communication is impossible. It establishes that the current concise projection implementation is not representation-preserving under the contract being tested.

No failed projection should be silently repaired, and the test should not be weakened merely to restore a green CI result.

## No-LLM constraint

No LLM performs projection, semantic evaluation, epistemic assignment, labeling, or repair.

## Evidence boundary

The result is limited to the tested structured projection. It does not establish unrestricted natural-language equivalence, learned communication failure, or failure of Cognitia's broader cognitive-transfer system. The cognitive-transfer job in the same workflow completed successfully.

## Next research question

First determine whether evidence identity is correctly defined as a mandatory invariant for every representation. If it is, revise the projection hypothesis so that even a concise surface retains a machine-observable evidence reference, then rerun the controlled experiment. The existing failure remains part of the evidence trail.
