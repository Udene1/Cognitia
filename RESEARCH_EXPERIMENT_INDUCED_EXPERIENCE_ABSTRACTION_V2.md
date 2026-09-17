# Induced Experience Abstraction v2

## Status

**Completed. The experiment was run on the representation-invariant branch and its CI artifact was inspected before merge.**

## Research question

Does representation invariance allow an induced experience abstraction to transfer across causal surface forms and revise after contradiction without structural IDs?

## Result

The v2 experiment did not provide the intended discriminator cleanly enough to establish transfer/revision. The abstraction engine still operates on a bounded surface-feature vocabulary (`question`, `causal`, `temporal`, uncertainty, negation, entity count and relation count). Representation-family invariance therefore improves the upstream relation signal, but it does not by itself establish that the abstraction engine can discover a stable event-level abstraction.

The contradiction case also exposed an important distinction: **support changing is not the same as the selected abstraction changing**. A revision mechanism may retain the same hypothesis while changing its evidence balance. The experiment therefore must record both.

## What this changes

The next experiment should not add more linguistic special cases or more feature families merely to obtain a positive transfer result.

Instead, Cognitia needs a more general intermediate representation whose identity is based on the structured relations/events produced by the language layer, while preserving candidate status and provenance. Then the experience mechanism can test whether two differently worded experiences refer to the same structural pattern without relying on question/statement surface labels.

The discriminator should include:

- held-out paraphrases with the same relation arguments;
- argument-role reversals as negative controls;
- changed outcome evidence for the same structural pattern;
- persistence of an abstraction after new experience;
- explicit lineage showing which experiences support or contradict it.

## Boundary

Current evidence supports a limited representation invariance result at the causal relation-family level. It does **not** establish semantic understanding, robust abstraction, learning, or generalization.
