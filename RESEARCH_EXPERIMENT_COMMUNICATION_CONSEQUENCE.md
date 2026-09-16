# Experiment 4: communicative consequence and adaptation

## Status

Research hypothesis / controlled experiment design. No result is implied by this document.

## Why this experiment follows

Experiments 1 and 2 established explicit objective- and recipient-conditioned communicative act selection. Experiment 3 exposed a representation-preservation failure, and Experiment 3A established a tested boundary in which evidence may be compacted only when its exact identity remains deterministically recoverable.

The next unresolved question is not whether Cognitia can select an act once. It is whether communication can become part of a cognitive loop in which what happens after an action becomes evidence about the action and changes a later decision.

The broader roadmap therefore remains intact. This experiment advances the communication route from:

```text
cognitive state → communication decision → representation
```

toward:

```text
cognitive state
    → communication decision
    → communication action
    → observed consequence
    → experience
    → policy/model revision
    → future communication decision
```

## Research question

> Can Cognitia record the consequence of a communicative action and use that experience to change a future communicative decision without changing the epistemic state merely to obtain a better outcome?

## Competing hypotheses

### H4-no-adaptation

Recording consequences does not change future communicative selection. The selector remains fixed.

### H4-experience-only

Cognitia can persist a structured communication experience, but the experience does not influence future decisions.

### H4-adaptive-policy

A communication experience can revise a policy/model state, and that revised state can change a later communicative decision.

### H4-epistemic-corruption

Adaptation changes the communicative act by silently changing claim identity, evidence identity, uncertainty, epistemic status, or verification requirements.

H4-epistemic-corruption is a failure condition, not a desired capability.

## Controlled variables

Keep fixed where possible:

- underlying cognitive state;
- communicative objective;
- recipient role;
- available communicative alternatives;
- epistemic commitments;
- evidence identities;
- uncertainty;
- verification requirement.

Vary:

- observed communication consequence;
- outcome signal;
- accumulated experience.

## What counts as learning in this experiment

The experiment does **not** call a pre-written rule such as:

```text
if previous_result == "stalled": choose EXPLAIN_UNCERTAINTY
```

learning.

A meaningful adaptation observation requires all of the following:

1. an initial policy state exists before the experience;
2. the system records an observed consequence tied to an actual decision;
3. a policy/model state changes as a result of the recorded experience;
4. a later decision is computed using the revised state;
5. the later decision differs from the pre-experience policy under the same decision context, or differs in a held-out structurally related context;
6. the changed decision preserves epistemic commitments;
7. the changed behavior can be reproduced from the recorded experience rather than from an undocumented hidden condition.

## Minimal experiment

Use two candidate acts for the same communicative objective and unresolved cognitive state.

1. Start with no learned preference.
2. Record an experience in which one selected act produces a negative communication outcome.
3. Record an experience in which another candidate act produces a positive outcome.
4. Revise the policy from those experiences.
5. Re-run selection for the same objective/context.
6. Inspect whether the revised policy changes the selected act.
7. Separately verify that the cognitive state, evidence, uncertainty, and verification requirement are unchanged.

The experiment should expose the policy delta and decision provenance rather than only returning the final act.

## Important control

Run the same decision through a fresh policy with no experiences. It must remain at the baseline behavior. This distinguishes experience-dependent adaptation from accidental changes in the selector.

## Held-out transfer check

After the direct adaptation case, test a structurally related context that was not itself used to train the policy. The purpose is to determine whether the learned preference is tied to a specific decision instance or can transfer through the policy's representation.

A held-out transfer result must be recorded separately from direct adaptation. It must not be assumed merely because the implementation shares code.

## Epistemic invariant

Communication adaptation may change **how Cognitia acts**, but it must not silently change **what Cognitia knows**.

Therefore every adapted decision must continue to pass the existing epistemic-preservation checks, including:

- no candidate → established promotion;
- no invented evidence;
- no evidence deletion from the semantic contract;
- no removal of uncertainty;
- no removal of required verification;
- no alteration of claim identity.

## Required observations

The CI/reproduction record must report:

- initial policy state;
- experience records;
- observed consequences;
- policy/model revision;
- baseline decision;
- adapted decision;
- held-out decision, if tested;
- epistemic-preservation result;
- whether adaptation actually depended on recorded experience;
- any regression or failure.

A green test suite without these observations is insufficient evidence for H4-adaptive-policy.

## Interpretation boundaries

If adaptation succeeds, the result establishes only a controlled stateful communication-policy adaptation capability. It does not establish general learning, general intelligence, natural-language understanding, or human-like social cognition.

If adaptation fails, the failure must be preserved. The next hypothesis should be derived from the observed failure rather than replacing the test with a weaker assertion.

## Roadmap relationship

Experiment 4 is one step in the larger Cognitia roadmap. It does not replace work on world modeling, causal reasoning, hypothesis management, cross-domain transfer, language, action, persistent knowledge, or broader learning. It tests one missing link: whether communication consequences can become experience that modifies future cognitive action selection.
