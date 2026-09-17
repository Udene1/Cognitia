# Research: communication consequence observation ordering

## Observation

The temporal-language experiment established that a single natural-language claim can be extracted without being converted into an explicit temporal relation, and the resulting proposition did not add a synthesis factor.

## Hypothesis

Unknown. The next test removes temporal language entirely. Two independent observations carry their ordering only in `observed_at` metadata. The question is whether the existing evidence machinery can reconstruct a usable relationship from the observation records themselves.

## Experiment

Hold the supported two-factor baseline constant. Compare two cases containing the same two event observations:

1. dependency timeout observed at 10:00, service collapse observed at 10:01;
2. dependency timeout observed at 10:01, service collapse observed at 10:00.

The event text contains no causal or temporal connective. No expected relationship, relevance label, target factor, interpretation, or communication-learning rule is supplied.

## Zero-handholding boundary

Cognitia receives the raw observations and their metadata through the existing research/evidence path. The experiment does not calculate or inject the relationship between timestamps.

## Result

CI run `35251840650` completed successfully.

Both cases produced zero extracted claims. The ordered case and the reversed-order case both retained the same two baseline synthesis factors:

- `Internal resource exhaustion`
- `Internal dependency failure`

Neither case changed the answer, factor set, or revision fingerprint. Reversing only the `observed_at` metadata therefore produced no observable change in the current evidence/synthesis path.

Recorded comparison:

- `ordered_claim_count: 0`
- `reversed_claim_count: 0`
- `factor_sets_differ: false`
- `answers_differ: false`
- `ordered_added_factor: false`
- `reversed_added_factor: false`

## Interpretation

The current evidence path does not extract standalone event propositions from these observations and does not use their `observed_at` metadata to reconstruct an ordering. The ordering information exists in the raw observation metadata, but it does not currently cross the claim-extraction boundary into synthesis.

This is a stronger boundary than the preceding temporal-language test: removing temporal language did not merely fail to produce a temporal relation; it produced no claim at all, and changing the recorded observation order was behaviorally inert.

The result does not justify adding a timestamp interpretation rule. It establishes that the existing observation-to-claim boundary currently does not consume this kind of structured temporal context.

## Provenance

- consequence interpretation: `observed`
- observation-order reconstruction: `observed_boundary`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`

## Next hypothesis

The next experiment should move away from the answer/synthesis path and test whether Cognitia's experience machinery can combine separately observed events into an experience without first requiring a natural-language causal claim. The test should expose multiple observations and their actual consequences, but provide no grouping, causal interpretation, or expected experience. Only the resulting experience artifact should tell us whether the system currently constructs anything from the sequence.
