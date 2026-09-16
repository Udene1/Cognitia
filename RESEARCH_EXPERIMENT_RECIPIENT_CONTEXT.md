# Experiment 2: Recipient/Context-Conditioned Communicative Action Selection

## Status

**Implementation prepared; CI evidence pending.**

## Motivation

Experiment 1 established a narrow controlled distinction: with the same cognitive state and recipient, changing the communicative objective changed the selected communicative act while epistemic commitments were preserved.

That result leaves a critical alternative explanation open: the selector may only be an objective lookup table. If recipient/context has no causal role, communication remains detached from interaction.

Experiment 2 therefore changes the recipient context while holding the underlying cognitive state and communicative objective constant.

## Research question

> Given the same underlying cognitive state and communicative objective, can Cognitia select different communicative actions as controlled recipient context changes, without changing the epistemic commitments being communicated?

## Controlled variables

Held constant:

- cognitive state;
- question;
- hypotheses;
- evidence;
- uncertainty;
- missing discriminating evidence;
- communicative objective (`INFORM`).

Varied:

- recipient role.

Controlled recipient roles:

- `OPERATOR` — needs the current operational state;
- `DECISION_MAKER` — needs decision-relevant uncertainty and reversible action support;
- `LEARNER` — needs explanation of why the evidence does not establish the conclusion.

## Expected observations

The current explicit experimental mechanism predicts:

```text
same state + INFORM + OPERATOR
    → REPORT_CURRENT_STATE

same state + INFORM + DECISION_MAKER
    → SUPPORT_DECISION_UNDER_UNCERTAINTY

same state + INFORM + LEARNER
    → EXPLAIN_UNCERTAINTY
```

The prediction is deliberately implemented explicitly. This is a capability exposure experiment, not a claim of learned recipient modeling.

## Epistemic invariant

Recipient adaptation may change selection and organization of communication, but must not alter the underlying warrant.

Therefore every recipient-conditioned decision must retain:

- the same cognitive state identity;
- the same uncertainty;
- no candidate-to-established upgrade;
- no unsupported strengthening;
- the same verification requirement when the underlying state remains unresolved.

## Failure interpretation

A failure is informative. Examples include:

- recipient changes but act does not change;
- act changes by recipient but epistemic status changes incorrectly;
- context is accepted but not represented in the decision record;
- adaptation occurs only through surface wording rather than communicative action;
- the mechanism requires hidden state not represented in the interaction context.

Failures must not be silently repaired in the experiment. They should become evidence for revising the hypothesis or experiment design.

## No-LLM constraint

No LLM performs recipient modeling, act selection, epistemic assignment, evaluation, labeling, or repair in this experiment.

## Evidence boundary

A passing controlled experiment can establish only that the explicit mechanism can condition act selection on the tested recipient variation. It cannot establish learned recipient modeling, general audience adaptation, or communication learning.

The next experiment after this one should test representation/surface projection while holding the selected communicative act fixed. Only after that should communication consequences be introduced as learning signals.
