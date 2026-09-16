# Adversarial Abstraction Stability v1

## Status

Completed. The experiment ran through the established `action-space-reduction-research` CI workflow, and the authoritative artifact was inspected.

## Research question

Does contradiction-driven abstraction narrowing remain stable under adversarial counterexamples, or does the mechanism overfit by repeatedly specializing?

## Protocol

Three contradictory experiences were introduced sequentially after the initial abstraction was induced.

No researcher-supplied structural IDs or expected abstraction were used.

The held-out experience remained fixed so that transfer could be observed while the abstraction trajectory changed.

## Observed trajectory

| Stage | Selected abstraction | Positive | Negative | Consistency |
|---|---|---:|---:|---:|
| Initial | `causal` | 3 | 0 | 1.0 |
| After contradiction 1 | `causal + temporal` | 1 | 0 | 1.0 |
| After contradiction 2 | `causal` | 3 | 2 | 0.2 |
| After contradiction 3 | `causal` | 3 | 3 | 0.0 |

The held-out experience remained relevant at every stage under the current structural matcher.

The artifact reported:

- initial broad abstraction: `true`;
- narrowing occurred: `true`;
- repeated narrowing: `false`;
- held-out transfer survived: `true`;
- support decreased: `true`.

## What the trajectory tells us

The first contradiction produced the specialization observed in v2: the broad `causal` abstraction was weakened, and the mechanism temporarily selected `causal + temporal`, which avoided that particular contradictory observation.

The second contradiction was deliberately chosen to attack that specialization. The mechanism did not continue narrowing. It returned to the broader `causal` abstraction, now with **3 positive / 2 negative** observations and consistency `0.2`.

A third contradiction drove the broad abstraction to **3 positive / 3 negative**, consistency `0.0`.

This is evidence against the simplest form of the overfitting hypothesis tested here: the mechanism did not endlessly specialize after every contradiction. Instead, specialization was temporary and was itself vulnerable to further contradictory evidence.

## Critical limitation

This still does **not** establish useful abstraction learning.

The current hypothesis space is researcher-defined feature combinations, and revision is deterministic counting. A return from a narrow abstraction to a broad one may reflect the mechanics of that hypothesis space rather than a meaningful conceptual judgment.

Also, `held_out_relevant=true` only means the selected abstraction's feature subset matches the held-out representation. It does not establish that the abstraction predicts a useful action or consequence.

## Research consequence

The next discriminator should connect abstraction revision to actual consequences and future action selection without researcher-supplied state IDs.

Specifically, the system should face a held-out problem, select an action because of an induced abstraction, observe the consequence, and then test whether that consequence changes later action selection on a structurally related but linguistically novel problem.

The key requirement is that abstraction is no longer evaluated only as a label. It must participate in the full loop:

`experience -> abstraction -> action -> consequence -> revised abstraction -> future action`.

That is the next boundary.
