# Causal Representation Invariance v1

## Status

**Completed. CI research artifact inspected from the latest head.**

The representation-invariance job succeeded and the artifact reported all four controlled surface forms converging to the same candidate relation family: `causal / caused`.

## Research question

Do equivalent causal surface forms converge on the same candidate relation family before experience abstraction?

This experiment directly follows PR #27, where experience abstraction failed because semantically related surface forms were represented differently.

## Protocol

Controlled variants expressed the same causal situation as:

1. a `why did ... after ...?` question;
2. an explicit `caused` statement;
3. a `because` construction;
4. a `what caused ...?` question.

The researcher defined the equivalence class for evaluation, but did not provide Cognitia's internal relation. The representation layer generated candidate relations and retained `confidence="candidate"`.

## Observed result

The CI artifact reported:

- all variants emitted a candidate causal relation: `true`;
- all used the normalized `caused` predicate: `true`;
- candidate confidence was preserved: `true`;
- relation-family shape converged: `true`.

The previous duplicate/incorrect interpretation of `What caused ...?` was removed. Explicit causal statements are now represented in the correct cause -> effect direction, and causal questions are not re-parsed by the generic statement matcher.

## What this establishes

The representation layer now has a limited invariance property: several syntactically different causal constructions converge on one explicit candidate relation family before abstraction induction.

This directly removes the specific representation mismatch that blocked the previous abstraction experiment.

## Remaining limitation

This is **not full semantic normalization**.

The relation family converges, but the relation arguments remain surface fragments. For example, `what caused` correctly records `<unknown-cause>` rather than inventing a cause, while the explicit and `because` variants preserve different textual fragments for the effect/cause arguments.

Therefore the result supports:

> surface-form invariance at the relation-family level

but not yet:

> identity/invariance of the complete underlying event structure.

We should not treat `caused` as proof that a causal relation is true. The representation remains a candidate interpretation.

## Research consequence

The next experiment can now return to experience abstraction without the exact blindspot exposed by PR #27. But it should be stronger than simply rerunning v1: the abstraction layer should consume the normalized relation family and test whether experience transfer survives syntactic variation **and** whether contradictory evidence can revise the induced abstraction.

The remaining question is whether this representation improvement actually changes future experience-conditioned behavior, not merely whether the parser passes its own invariance test.
