# Experience Loop and Structural Transfer

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

`tests/ci/structural_transfer_research.py` runs the existing `AdaptiveOpenResearch` controller against held-out questions with structurally paired evidence states:

- supported claim;
- conflicting claims;
- uncertain claim;
- no usable claim.

Surface questions differ within each structural pair. The controller, round budget, acquisition limits, and extraction limits remain fixed. No question-specific action mapping is encoded.

The experiment records the first evidence state and the actual second action, information need, provenance, and parent action. It compares the observed abstract action-purpose category across held-out questions rather than prescribing a concrete query.

### Interpretation boundary

A consistent action category across changed questions would be evidence that the existing evidence-conditioned mechanism transfers across those held-out states. A failure to transfer would be evidence against that hypothesis. Neither result establishes learning because the current routing logic remains researcher-authored.

## Next discriminator

The next experiment after structural transfer is experience-conditioned future behavior:

1. run a problem and record action + expected consequence;
2. expose the actual consequence;
3. update the cognitive state through an explicit experience record;
4. present a new held-out problem where that experience could matter;
5. compare behavior against an experience-absent control;
6. repeat with a changed surface problem.

The experiment must establish that the experience, rather than a scenario-specific rule, accounts for the behavioral change before calling the result learning.

## Research standard

CI protects reproducibility and instrumentation. The generated research artifact is the behavioral observation. Passing CI is not itself a cognitive result.
