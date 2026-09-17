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

CI run `35251362795` completed successfully.

The temporal consequence produced one extracted claim:

> `The internal dependency timeout was observed before the service collapse.`

However, the extractor represented it with relation `was` and `temporal_markers: []`; the timing language was therefore preserved in the proposition but not converted into an explicit temporal relation by the current claim extractor.

The temporal case did not add a synthesis factor. Its factor set remained:

- `Internal resource exhaustion`
- `Internal dependency failure`

The unrelated control also added no factor and produced the same answer. Both cases changed the evidence fingerprint because the augmented evidence/genealogy changed, but neither changed the synthesized conclusion.

The recorded comparison was:

- `temporal_claim_extracted: true`
- `temporal_added_factor: false`
- `unrelated_added_factor: false`
- `answers_differ: false`

## Interpretation

The current evidence path can ingest the temporal recipient consequence as an ordinary extracted claim, but it does not currently recover the temporal structure from the language and does not turn that claim into a new synthesis factor.

This is a real boundary of the current substrate. It does not establish that temporal evidence is unusable in principle, nor does it justify inserting a temporal interpretation rule merely to make the experiment succeed.

The result also sharpens the boundary exposed by PR #54: explicit causal language can reach synthesis as a recognized causal claim, while this temporal formulation currently reaches only proposition-level evidence.

## Provenance

- consequence interpretation: `observed`
- temporal evidence integration: `observed_boundary`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`

## Next hypothesis

The next experiment should remove the remaining linguistic crutch in a different direction: test whether Cognitia can derive a usable relationship from multiple independent observations whose ordering must be reconstructed from their recorded observation metadata, rather than from a temporal phrase embedded in a single natural-language claim. No expected relationship or target factor should be supplied.
