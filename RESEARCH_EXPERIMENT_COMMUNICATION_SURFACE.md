# Experiment 3: Representation-Preserving Communication

## Status

**Implementation prepared; CI evidence pending.**

## Research question

Given one selected communicative act, can Cognitia express that act through different explicit representations without changing claims, evidence, uncertainty, epistemic status, or verification requirements?

## Controlled variables

Held constant:

- cognitive state;
- recipient;
- communicative objective;
- selected communicative act;
- claim set;
- evidence set;
- uncertainty;
- verification requirement.

Varied:

- representation: `STRUCTURED`, `CONCISE`, `EXPLANATORY`.

## Expected observation

Every projection must preserve the semantic communication contract exactly while its payload organization changes.

This experiment deliberately uses structured representations rather than asking an LLM to judge whether prose "means the same thing". That keeps semantic preservation experimentally identifiable.

## Failure interpretation

A failure is evidence if a projection:

- changes the selected act;
- drops or invents a claim;
- changes epistemic status;
- changes evidence identity;
- removes uncertainty;
- removes a required verification condition; or
- becomes equivalent only because an external language model silently repairs it.

No failed projection should be silently repaired.

## No-LLM constraint

No LLM performs projection, semantic evaluation, epistemic assignment, labeling, or repair.

## Evidence boundary

A successful experiment establishes only representation invariance for the tested structured projections. It does not establish unrestricted natural-language generation, semantic equivalence across arbitrary media, or learned communication.

## Next step

If the preservation invariant survives, introduce observable communication consequences and test whether Cognitia can learn a policy that changes from experience and transfers to held-out interactions.
