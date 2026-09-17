# Research experiment: experience-to-state provenance boundary

## Research question

Can experience modify active cognitive state while remaining distinguishable from established knowledge and still requiring epistemic testing?

## Design

This experiment deliberately crosses the boundary identified by the experience-state-transition audit, but it does **not** make `Experience.state_update` authoritative.

A confirmed or unresolved experience may contribute an explicitly experience-derived hypothesis to the active `CognitiveState`. A refuted experience contributes uncertainty instead. Neither path writes into `knowledge_ids`.

The transition therefore changes cognition without collapsing provenance:

```text
Experience
   -> provenance-preserving transition
   -> active CognitiveState
      - knowledge remains knowledge
      - experience remains experience-derived
      - refutation remains uncertainty
      - epistemic testing remains required
```

## Why this is the right boundary

The research question is not whether Cognitia can copy `state_update` into a state object. That would only demonstrate mutation.

The meaningful question is whether Cognitia can **learn from experience without treating experience as truth**.

The experiment therefore asserts four properties:

1. active state can change because of experience;
2. established knowledge is not overwritten or expanded merely because experience was observed;
3. refuted experience does not become knowledge;
4. the resulting state remains marked for epistemic testing.

## Current limitation

This experiment is a capability boundary, not yet proof that the full Cognitia reasoning loop consumes the resulting state. The next experiment must feed the resulting state into the existing operation-selection / epistemic path on a genuinely new problem.

## Next research boundary

Construct a new problem that is structurally related to a prior experience but not identical to it. Give Cognitia a state containing:

- experience-derived expectations;
- independently established knowledge;
- self-model information;
- other-agent/world-model information;
- unresolved uncertainty.

Then observe whether its epistemic process keeps those sources distinguishable while deciding what needs to be investigated.
