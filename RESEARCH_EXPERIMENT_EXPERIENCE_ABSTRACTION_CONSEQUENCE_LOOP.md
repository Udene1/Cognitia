# Experience → Abstraction → Consequence Loop v1

## Status

**Completed. CI run `35122941239` succeeded and the nested research artifact was inspected directly.**

The experiment ran through the established `experience-blindspot-research` workflow at the latest PR head.

## Research question

Can an induced abstraction participate in future action selection, then be revised by an observed consequence and affect a later linguistically novel action decision?

## Protocol

No researcher-supplied structural IDs or expected actions were used.

Available operations were `search`, `inspect`, `compute`, and `reason`.

The trajectory was:

1. no experience;
2. confirmed experience on a causal problem;
3. held-out causal problem with changed surface wording;
4. observed refutation of the selected action on the held-out problem;
5. later causal problem with another changed surface;
6. unrelated specificity control.

## Observed trajectory

### 1. Experience absent

The abstraction was empty. All candidate operations scored `0.0`; deterministic tie-breaking selected `compute`.

### 2. Confirmed experience

The induced abstraction was `("causal",)`.

The `search` operation received `+0.500` from the confirmed experience and was selected over the zero-scored alternatives.

### 3. Held-out consequence contradicts search

The same causal abstraction matched both the confirmed seed and the refuted held-out experience.

Their contributions cancelled:

- confirmed: `+0.000` after abstraction consistency reached `0.0`;
- refuted: `-0.000`;
- `search`: total `0.0`.

The selector therefore returned to the deterministic baseline `compute` for the later causal problem.

### 4. Specificity control

The unrelated material-selection problem did not match the causal abstraction. It also selected the baseline `compute` action.

## CI observations

The artifact reports:

- experience changes future action: `true`;
- contradicted consequence changes future action: `true`;
- later problem surface differs: `true`;
- specificity control unchanged: `true`;
- full loop executed: `true`.

## What this establishes

For the explicit deterministic mechanism now implemented, an induced abstraction can sit between prior experience and future action selection without researcher-supplied structural IDs.

An observed consequence can change the future action on a later linguistically novel problem.

The same abstraction also remains specific enough in this test not to affect an unrelated problem.

This is the first experiment in the current line that closes the causal loop rather than evaluating abstraction as a standalone label:

`experience -> abstraction -> action -> consequence -> revised abstraction -> future action`.

## Critical limitation

The mechanism is still explicitly designed:

- abstraction induction is a bounded feature-combination search;
- action influence is an explicit score based on abstraction consistency and operation overlap;
- the consequence is represented by a supplied epistemic outcome.

The result therefore does not establish autonomous learning, semantic understanding, or world-grounded causal knowledge.

There is also an important edge revealed by the trajectory: when confirmed and refuted evidence exactly cancel, the system does not choose a new epistemic strategy. It falls back to the deterministic baseline `compute` because all action scores tie.

That fallback is now the next blindspot boundary.

## Research consequence

The next discriminator should ask whether **uncertainty created by contradictory experience becomes an explicit state that changes what Cognitia does next**, rather than merely cancelling a score and falling back to a fixed tie-breaker.

The system should distinguish at least:

`known preference -> contradicted preference -> unresolved conflict`

and test whether unresolved conflict itself generates a new action objective, without the researcher prescribing that objective.

The next experiment should therefore target **conflict-state generation**, not another action-ranking constant.
