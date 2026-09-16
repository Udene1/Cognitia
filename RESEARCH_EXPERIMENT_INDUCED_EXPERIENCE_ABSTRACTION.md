# Induced Experience Abstraction v1

## Status

**Completed. CI experiment job succeeded and the research artifact was inspected.**

The engineering run passed, but the research discriminators did not. This is the result, not a failed CI gate.

## Research question

Can Cognitia construct a transferable structural abstraction from experience surfaces without researcher-supplied state identifiers, and revise its support after contradiction?

## Protocol

The engine received only raw problem surfaces, actions and observed epistemic outcomes. Researcher-supplied `hypothesis_ids` and `uncertainty` were deliberately ignored.

Candidate abstraction families were generated from the existing language representation layer: question/statement, causal/non-causal, temporal/non-temporal, uncertainty, negation, entity count and relation count.

No expected abstraction was supplied.

## Observed result

The artifact reported:

- abstraction induced: `true`;
- structural IDs absent: `true`;
- specificity control: `true`;
- held-out transfer: `false`;
- contradiction changed support: `false`.

The top pre-contradiction abstraction was `("causal",)` with one positive observation.

However, the first training experience and the held-out experience were natural-language causal questions such as “Why did ... after ...?” The language representation classified both as `non_causal`; the explicit causal training statement was the only item classified as `causal`.

Therefore the induced abstraction did not recognize the held-out question as structurally equivalent to the explicit causal statement.

The contradiction also did not alter the top abstraction because the contradictory experience was classified `non_causal`, so it did not match the selected `causal` hypothesis.

## What the failure tells us

This is a real blindspot in the current abstraction pipeline:

> **The transfer mechanism is downstream of representation invariance. If two semantically related experiences arrive in different linguistic forms and the representation layer assigns them different structural features, abstraction induction cannot discover their equivalence.**

The failure occurred without researcher-supplied structural IDs. That is important evidence: removing hand-authored equivalence exposed a dependency that the previous experiment hid.

The current language representation recognizes explicit causal predicates (`caused`, `led to`, etc.) but does not currently represent a `why did X after Y?` question as a candidate causal relation. The experiment therefore exposed a representational gap rather than demonstrating that the induced abstraction itself is incapable of transfer.

## Boundary

We must not patch this by adding a special-case `why did ... after ... -> causal` rule merely to make this experiment pass.

The next discriminator should test **representation invariance** across multiple linguistic realizations of the same underlying relation, including questions, statements, temporal constructions and explicit causal predicates. The representation layer should emit candidate interpretations with epistemic uncertainty; the experiment should then determine whether a stable abstraction survives those alternative representations.

Only after that boundary is understood should experience abstraction induction be rerun.

## Research consequence

PR #27 should retain this result as evidence. The next experiment should attack the representation blindspot directly rather than stacking another abstraction rule on top of it.
