# Research: communication consequence temporal evidence

## Observation

PR #54 showed that a recipient consequence can change the synthesized evidence state when the extracted claim contains an explicit causal relationship that the existing synthesis engine recognizes.

## Hypothesis

Unknown. The next test removes the explicit causal connective while retaining a concrete temporal consequence. It asks whether the existing evidence machinery can use timing information without being handed a causal interpretation.

## Experiment

Hold the supported two-factor baseline from PR #54 constant. Compare:

1. a recipient consequence stating that an internal dependency timeout was observed before the service collapse, plus an unchanged CPU observation;
2. the same unrelated dashboard consequence used as a control.

No causal relationship, relevance label, expected interpretation, or target state is supplied.

## Zero-handholding boundary

Cognitia receives only the raw recipient observations and whatever claims the existing extractor produces.

## Result

To be completed from CI output. Artifact: `.ci/communication-consequence-temporal-evidence.json`.

## Interpretation boundary

The key boundary is whether temporal evidence becomes an extracted claim and whether that claim is sufficient for the existing synthesis engine to construct a factor. A failure here is evidence about the current reasoning substrate, not a reason to insert a causal interpretation rule.

## Provenance

- consequence interpretation: `observed` until actual result
- temporal evidence integration: `unknown`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`

## Next hypothesis

Only after the actual result is inspected.
