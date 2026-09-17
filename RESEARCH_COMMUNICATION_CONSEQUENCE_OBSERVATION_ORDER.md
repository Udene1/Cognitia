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

To be completed from CI output.

## Interpretation boundary

The key question is whether changing only observation metadata can change extracted evidence or synthesized state. If it cannot, that is a boundary of the current evidence substrate, not a reason to insert a timestamp-to-causality rule.

## Provenance

- consequence interpretation: `observed`
- observation-order reconstruction: `unknown`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`

## Next hypothesis

Only after the actual result is inspected.
