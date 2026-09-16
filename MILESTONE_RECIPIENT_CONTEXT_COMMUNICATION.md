# Milestone: Recipient/Context-Conditioned Communication

## Status

**Experiment 2 implementation prepared; CI validation pending.**

## Research question

Given the same underlying cognitive state and communicative objective, can Cognitia select different communicative actions as controlled recipient context changes while preserving epistemic commitments?

## Why this experiment follows Experiment 1

Experiment 1 showed objective-dependent act selection. It did not establish that communication is genuinely interaction-conditioned because the recipient was held constant.

Experiment 2 therefore varies recipient role while keeping the state and objective fixed. This is the smallest next experiment that can discriminate between:

```text
communication = objective lookup
```

and

```text
communication = action selection conditioned by cognitive + interaction state
```

## Controlled result target

For the unresolved controlled state and objective `INFORM`:

```text
OPERATOR
    → REPORT_CURRENT_STATE

DECISION_MAKER
    → SUPPORT_DECISION_UNDER_UNCERTAINTY

LEARNER
    → EXPLAIN_UNCERTAINTY
```

The same unresolved uncertainty and verification requirement must remain present across all three decisions.

## Implementation

The communication state now records a small explicit `RecipientRole` and `InteractionContext`. The selector uses that controlled context to choose the communicative act. This is deliberately deterministic and inspectable.

The implementation does not claim a learned recipient model.

## Evidence required before milestone completion

CI must demonstrate:

- all existing tests still execute;
- the new recipient-context tests observe the predicted act differences;
- epistemic-preservation checks continue to pass;
- the recipient context is retained in the structured decision;
- the existing cognitive-transfer path remains operational.

The exact observed CI behavior will be appended after the run rather than inferred from code inspection.

## Next step if validated

Hold the selected act fixed and introduce representation/surface projection. Test whether different representations preserve the same communicative act, claims, evidence, uncertainty, and verification requirement.
