# Experience Loop and Structural Transfer

## Status

**Structural-transfer experiment executed; result is partial transfer evidence, not learning evidence.**

## Purpose

Cognitia's research frontier is no longer the existence of isolated capabilities. The question is whether state produced by one capability can causally alter another capability's behavior, persist as experience, generalize to a new problem, and eventually improve future behavior.

The working process is:

`cognitive state → experience → interpretation → hypothesis → action → consequence → updated state → future action`

The repository must distinguish implementation mechanisms from evidence that these mechanisms learn or self-organize.

## New substrate

`cognitia.experience` introduces explicit, auditable records for:

- the state immediately before an action;
- the selected action and rationale;
- the expected consequence;
- the observed consequence and epistemic outcome;
- whether an expectation discrepancy occurred;
- the resulting state;
- provenance.

`ExperienceLedger` is append-only and deterministic. It does not infer abstractions, choose actions, or claim learning. Its purpose is to make experience available as a measurable state transition rather than collapsing it into a generic knowledge record.

## Structural-transfer experiment

`tests/ci/structural_transfer_research.py` runs the existing `AdaptiveOpenResearch` controller against held-out questions with paired evidence-state structures:

- one supported candidate claim;
- two candidate claims with opposite polarity;
- one uncertain claim;
- no extracted claim.

Surface questions differ within each pair. The controller, round budget, acquisition limits, and extraction limits remain fixed. No question-specific action mapping is encoded.

The experiment records the observed first-state structural signature and the actual second information need/action, including provenance and parent linkage.

### 2026-09-16 observation

The structural-transfer workflow executed successfully. Unit tests also passed on the experiment head, but those are engineering evidence only.

Observed information-need kinds:

- supported → `independent_evidence`;
- opposite-polarity two-claim state → `independent_evidence`;
- uncertain → `independent_evidence`;
- no extracted claim → `evidence_acquisition`.

Within every paired structural condition, the same abstract information-need kind appeared across the changed surface questions. This is evidence that the current controller's evidence-conditioned transition is reproducible across these held-out question pairs.

However, several structurally different states collapsed to the same `independent_evidence` category. In particular, the two opposite-polarity claims were not recognized as a conflict by the current claim-clustering layer (`conflict=false` in the observed state). Therefore the experiment does **not** establish that the controller represents those distinctions at the level needed for differentiated action selection.

The experiment also exposed an instrumentation lesson: `SearchAction.purpose` was `direct evidence` across all cases and therefore was not a useful discriminator. The research measurement was corrected to inspect the actual `ResearchInformationNeed.kind` and the preceding evidence-state signature.

### Interpretation boundary

The result supports a narrower statement:

> The existing researcher-authored evidence-conditioned research mechanism transferred the same information-need category across changed questions for each tested structural pair.

It does not establish learned cognition. The routing rules are explicitly implemented, and distinct evidence states can still collapse to the same action category.

## Next discriminator: experience-conditioned future behavior

The next experiment should now use the new `Experience` substrate rather than adding another isolated capability:

1. expose a pre-action cognitive state;
2. select and record an action without a scenario-specific experience rule;
3. record an expected consequence;
4. expose an independently controlled actual consequence;
5. record discrepancy and update state through `Experience`;
6. present a new held-out problem where the prior consequence could be relevant;
7. compare against an experience-absent control;
8. repeat with changed surface details.

The critical observation is whether prior experience changes later behavior in a way that cannot be explained by the existing static routing rules.

Only that kind of result begins to address:

`experience → changed future behavior`.

## Research standard

CI protects reproducibility and instrumentation. The generated research artifact is the behavioral observation. Passing CI is not itself a cognitive result.
