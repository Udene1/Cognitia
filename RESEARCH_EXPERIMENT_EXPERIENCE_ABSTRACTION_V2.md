# Experience Abstraction v2

## Status

Completed on `main` after PR #29 merge. The authoritative trajectory artifact was produced by CI run `35122252845`, job `induced-experience-abstraction-v2`, and inspected directly.

## Research question

Does representation invariance allow an induced experience abstraction to transfer across causal surface forms and revise after contradiction without structural IDs?

## Observed result

The artifact reports:

- abstraction induced: `true`;
- top abstraction was `("causal",)`;
- held-out transfer: `true`;
- specificity control: `true`;
- structural IDs absent: `true`;
- original abstraction support changed after contradiction: `true`;
- selected abstraction changed after contradiction: `true`;
- contradiction caused narrowing: `true`.

Before contradiction, the broad `causal` abstraction had **3 positive / 0 negative** observations and consistency `1.0`.

After a contradictory causal experience, the original `causal` abstraction became **3 positive / 1 negative**, consistency `0.5`.

The selector then preferred a narrower `("causal", "temporal")` abstraction with **1 positive / 0 negative**, consistency `1.0`.

The held-out `what caused` question matched the broad causal abstraction before contradiction. The unrelated non-causal material question did not.

## What this establishes

Removing researcher-supplied structural IDs did not prevent abstraction induction once the representation layer normalized the relevant causal surface forms.

The induced abstraction transferred across a held-out linguistic form and rejected the tested unrelated control.

Contradiction did affect the original abstraction's support. More importantly, the mechanism did **not** simply stop using the abstraction. It moved from the broad `causal` hypothesis to a narrower `causal + temporal` hypothesis whose observed support had not yet been contradicted.

That is the first clear evidence in this sequence that the implemented system can change the abstraction it uses after new evidence, rather than only changing the score of a fixed abstraction.

## Critical limitation

We cannot yet call this learning.

The narrowing behavior may be useful abstraction revision, but it may also be **overfitting by feature specialization**: when the broad abstraction was contradicted, the deterministic hypothesis generator could select a narrower subset that happened to avoid the contradictory example.

The current engine does not yet test whether that narrower abstraction survives new counterexamples, transfers beyond the feature combination that produced it, or represents a causally meaningful distinction.

The important next discriminator is therefore:

> **Can an abstraction that specializes after contradiction survive adversarial held-out counterexamples without endlessly narrowing itself around individual experiences?**

The next experiment should attack this directly. It should measure abstraction stability, generalization, and resistance to contradiction-driven overfitting. It should not add another scoring rule merely to reward the observed narrowing.

## Interpretation boundary

This is evidence about the implemented deterministic abstraction mechanism over candidate language representations. It does not establish semantic understanding, autonomous learning, or truth of the extracted causal relations.
