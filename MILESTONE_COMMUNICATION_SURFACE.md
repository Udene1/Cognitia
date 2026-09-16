# Milestone: Representation-Preserving Communication

## Status

**Experiment 3 implementation prepared; CI validation pending.**

## Question

Can Cognitia project one selected communicative act through different representations while preserving the exact communication contract?

## Implementation

The communication layer now separates:

```text
cognitive state
    ↓
communicative act selection
    ↓
CommunicationProjection
    ↓
representation surface
```

Three controlled representations are exposed: `STRUCTURED`, `CONCISE`, and `EXPLANATORY`.

The projection carries the selected act, claims, omitted claims, epistemic status, evidence, uncertainty, and verification requirement alongside its representation-specific payload.

## Validation requirement

CI must show that all representations preserve those fields while their payload organization differs, and that the existing communication and cognitive-transfer tests remain operational.

The exact observed behavior will be recorded after CI. A CI pass alone will not be treated as the research result.

## Evidence boundary

This experiment does not test learned communication or unrestricted natural-language equivalence. It tests whether a representation layer can be made explicitly accountable for preserving an already-selected communicative contract.

## Next direction

If validated, communication consequences become the next discriminating variable. The goal is to test whether experience can alter communicative policy rather than merely exercising another developer-authored mapping.
