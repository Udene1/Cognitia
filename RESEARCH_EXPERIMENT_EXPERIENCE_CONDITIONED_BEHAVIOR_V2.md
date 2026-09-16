# Experience-Conditioned Future Behavior v2

## Status

**Completed. CI run 35121156928 succeeded.** The research artifact was inspected after CI completion: `experience-conditioned-behavior-v2`.

CI success is only the engineering gate. The findings below come from the generated trajectory artifact.

## Research question

Does recorded experience alter future action selection on a held-out problem while remaining structurally specific and defeasible when contradictory evidence arrives?

This is the next discriminator after the structural-transfer experiment and the first experience-blindspot implementation. The objective is to test whether experience is actually part of the future decision state rather than merely retrievable metadata.

## Protocol

The researcher supplies only:

- a cognitive state structure;
- a set of operations the environment permits;
- the experimental conditions;
- the observables.

`StateActionGenerator` constructs candidate actions from the state. No condition supplies an expected winning action.

`ExperienceGeneratedActionSelector` ranks those generated actions using experience as defeasible evidence. It compares structural state signals and operation overlap; it does not contain scenario-specific problem -> action mappings.

Conditions:

1. experience absent baseline;
2. confirmed prior experience present;
3. the same prior experience contradicted by refuting experience;
4. held-out surface problem with the same structural state;
5. specificity control with a different structural state;
6. recovery episode after contradiction;
7. later independent episode to test persistence.

## Observed trajectory

The CI artifact recorded these selected operations:

| Condition | Selected operation |
|---|---|
| Experience absent | `compute` |
| Confirmed experience present | `search` |
| Confirmed + refuted experience | `compute` |
| Held-out transfer | `compute` |
| Unrelated structural state | `compute` |
| Recovery after contradiction | `compute` |
| Later episode | `compute` |

The confirmed experience added a `+0.500` contribution to `search`. The refuting experience added `-0.500`, cancelling that contribution and returning selection to the baseline `compute` operation.

The held-out problems changed their surface wording but retained the same structural hypothesis/uncertainty signals. The effect transferred. The unrelated material-selection problem did not inherit the experience effect.

The artifact reports all seven discriminators as observed:

- influence: `true`;
- defeasibility: `true`;
- transfer: `true`;
- specificity: `true`;
- recovery: `true`;
- persistence: `true`;
- novelty after conflict: `true`.

## What this establishes

Within this implementation, prior experience can become causally relevant to a later generated-action decision. The effect is not merely that an experience record is retrievable: changing the ledger changes the selected operation.

The same mechanism also demonstrates a limited form of defeasibility: confirmed experience can push selection toward an operation, while contradictory experience removes that preference and restores the non-experience baseline.

The effect transfers across changed problem surfaces when the structural state representation is held constant, and it does not transfer to the tested unrelated structural state.

The post-contradiction behavior persists across the later tested episode.

## Important limitation discovered

This is **not yet evidence that Cognitia learned a useful action from the world**.

The mechanism currently makes the experience effect explicit in the selector: state similarity + operation overlap + outcome weighting. The experiment therefore demonstrates a designed experience-conditioned decision rule, not discovery of that rule by Cognitia.

There is also a strong deterministic prior in the baseline: with the tested generated candidate ordering, `compute` wins ties. The experiment demonstrates how experience moves the decision away from that baseline; it does not establish that `compute` is substantively appropriate for the problems.

The current experience representation also records the previous action as a string and matches it against operation capability terms. That is a deliberately small mechanism, not a learned semantic model.

## Research consequence

The next problem is therefore not to add more hand-authored rules to make this mechanism appear more intelligent.

The next discriminator should test whether Cognitia can **construct and revise the abstraction that makes experience transferable**, rather than receiving structural identity (`hypothesis_ids`, `uncertainty`) from the researcher.

In other words:

> We have shown that an explicit experience representation can alter future behavior. Now remove the researcher's structural equivalence and test whether Cognitia can discover, preserve, challenge, and revise the features that make two experiences relevant to one another.

That is the next blindspot boundary.

## Anti-handholding boundary

The harness must not encode `if experience X then action Y`.

The previous action is recorded as an observed event. The next selector receives the ledger and independently ranks generated candidates. The experiment therefore measures the implemented mechanism's trajectory instead of comparing it against researcher-provided expected actions.

## Interpretation boundary

The result establishes only that this deterministic mechanism can use structured prior experience as defeasible evidence for future action selection under the tested conditions. It does not establish general cognition, autonomous learning, or cross-domain abstraction.

The next experiment must attack the remaining researcher-supplied structural abstraction rather than stack another selector rule on top of it.
