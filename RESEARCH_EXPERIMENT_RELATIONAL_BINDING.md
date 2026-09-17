# Relational Binding — Research Record

## Question

Can experience transfer across domains when lexical identity is abstracted but repeated-argument binding is preserved?

## Why this experiment exists

The preceding structural-experience experiment showed that a single causal relation could transfer across domains and influence candidate scores, but the representation deliberately discarded argument identity. That created a boundary: single-relation structure could not distinguish different bindings.

The next discriminator was therefore to test a multi-relation structure where the important information is not the words used for the entities, but whether the same entity participates in multiple relations.

## Protocol

Training:

`The database outage caused the payment queue to stall. The database outage reduced worker throughput.`

Held-out, binding-preserving:

`The mirror coating change caused the telescope image to degrade. The mirror coating change reduced optical throughput.`

Binding-rewired control:

`The mirror coating change caused the telescope image to degrade. The optical throughput reduced the mirror coating change.`

Controls:

- lexical argument identity is not used for matching;
- training and held-out domains differ;
- candidate order is reversed;
- Cognitia generates the training action;
- no expected action, hypothesis identifiers, or uncertainty labels are supplied;
- no scenario-specific routing is used.

## Representation change

Structural experience signatures now include a canonical binding pattern. Argument strings are converted to locally assigned IDs independently for each input. Only repeated-argument topology is compared.

For the training and binding-preserving held-out states the observed topology was:

`caused: 0 -> 1`

`reduced: 0 -> 2`

For the binding-rewired control it was:

`caused: 0 -> 1`

`reduced: 2 -> 0`

The lexical entities themselves were never compared.

Multi-relation experience relevance now requires the complete structural signature to match rather than accepting partial local relation overlap.

## Observed result

The CI artifact showed:

- binding-preserving structural signature: **true**;
- held-out experience considered relevant: **true**;
- binding-rewired structural signature: **false**;
- binding-rewired experience considered relevant: **false**;
- lexical argument identity used for matching: **false**.

The binding-preserving held-out candidates received the experience and their scores increased (`1.00 / 0.90 / 0.88` to `1.25 / 1.15 / 1.13`), while the binding-rewired candidates received no experience contribution and retained their baseline scores.

The selected action did not change in the held-out case. Therefore the experiment establishes a stronger result than simple lexical transfer, but not yet experience-driven action switching.

## What changed in our understanding

Cognitia now has evidence, within this bounded mechanism, that it can abstract away lexical entity identity while retaining repeated-argument topology across a different domain. It also rejects a structurally rewired state that shares the same local relation families.

This is still not evidence of semantic understanding or learning. It is evidence that the current representation can encode and compare a particular form of relational binding.

The unchanged selected action remains important. Experience is reaching the selector and changing scores, but the current candidate priorities can dominate the experience contribution. Relevance transfer and behavioral consequence are therefore separate research questions.

## Next discriminator

Do not add more representation features yet. Test whether the bound experience can produce a downstream consequence.

Use a multi-step episode with:

1. a binding-preserving held-out state;
2. a binding-rewired control;
3. a confirmed experience in the first step;
4. a changed or contradictory outcome in a later step;
5. explicit experience lineage showing which support or contradiction affected the later information need/action;
6. no researcher-selected expected action.

The key question becomes: **does the bound structure change what Cognitia needs to investigate next, rather than merely whether the experience is marked relevant?**

## Reproducibility

The experiment and focused tests passed in CI on commit `aeb160007260b371ca7911f1cf689474a448ac69`. The generated CI artifact was inspected before this record was written.
