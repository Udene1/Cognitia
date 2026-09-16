# Milestone: Deterministic Communicative Cognition

## Status

**Experiment 1 implementation complete and CI-validated.**

This milestone records the first executable step in investigating communication as a cognitive capability.

## Research question

> Given the same underlying cognitive state, can Cognitia select different communicative acts according to communicative objective while preserving epistemic commitments?

## Evidence

PR #8: `Begin deterministic communicative cognition experiment`

CI workflow run: **35056983672**

Relevant CI outcomes:

- `test`: **success**
- `cognitive-transfer`: **success**
- durable runner-boundary state restored: **3 SQLite databases**
- cross-run recovery: **1 prior run recovered**
- answer-core diagnostics artifact: **uploaded successfully**
- no LLM dependency in the communication implementation

The unit-test suite contains five communication-specific tests covering objective-dependent act selection, epistemic preservation, clarification, capability-limited partial results, and rejection of candidate-to-fact upgrades. The unit-test job completed successfully.

## Observed result

With the same underlying cognitive state and the same recipient (`operator`), changing the communicative objective selected four distinct acts:

```text
INFORM
    → REPORT_CURRENT_STATE

INVESTIGATE
    → PROPOSE_DISCRIMINATING_TEST

DECISION_SUPPORT
    → SUPPORT_DECISION_UNDER_UNCERTAINTY

TEACH
    → EXPLAIN_UNCERTAINTY
```

The preservation tests did not permit an unresolved hypothesis to become established merely because it was selected for communication.

Additional controlled cases showed:

```text
ambiguous interaction
    → REQUEST_CLARIFICATION

insufficient capability
    → REPORT_LIMITATION_WITH_PARTIAL_RESULT
    → verification required
```

An explicit negative test attempted to convert a supported candidate into an established fact. The preservation mechanism rejected the transformation.

## Interpretation

The result supports the narrower engineering/research proposition that **communicative objective can be represented independently from underlying epistemic state and can influence communicative-act selection without changing epistemic warrant**.

This is not evidence that Cognitia has learned communication.

The current mapping is explicitly implemented. Therefore the result demonstrates an executable representation of the distinction, not emergence or learning of the distinction.

## What this milestone establishes

- Communication can be represented as an action-selection layer rather than only as prose.
- Communicative objective can vary while the underlying cognitive state remains fixed.
- Epistemic preservation can be tested before surface realization.
- Clarification and capability-limited partial communication can be represented as legitimate actions.
- The communication research path can proceed without an LLM performing the capability under investigation.
- The research provenance is now linked from observation and hypothesis to executable implementation and CI evidence.

## What this milestone does not establish

- learned communication policy;
- recipient modeling;
- audience adaptation;
- coherent unrestricted natural-language communication;
- composition of multiple communicative acts;
- communication consequence learning;
- generalization to unseen objectives or contexts;
- discovery of communicative acts rather than use of developer-defined acts.

## Next experiment

Do not expand the taxonomy merely because the first test passed.

The next discriminating experiment should vary **interaction context/recipient** while holding the cognitive state and communicative objective controlled. This will test whether the selected communicative action depends on who the communication is for and what the interaction permits.

After that, introduce a controlled surface projection and test whether the representation preserves the selected act and epistemic commitments.

Only then should we introduce interaction consequences and ask whether Cognitia can learn communication policies from experience.

The intended research progression remains:

```text
observation
→ hypothesis
→ controlled experiment
→ CI evidence
→ failure/success analysis
→ revised hypothesis
→ next experiment
→ candidate learned policy
→ independent reproduction
→ transfer
→ validation
```

## No-LLM invariant

For the foreseeable research horizon, no LLM is to perform Cognitia's cognition, communicative-act selection, epistemic assignment, experiment evaluation, training-label creation, or silent repair in this research path.

Any future change to this invariant must be documented as a research-method change and experimentally justified.
