# Research: communication consequence evidence integration

## Observation

PR #52 showed that raw recipient-consequence content can change `DocumentClaimExtractor` output, but neither tested consequence changed the `AnsweringCore` fingerprint. The current revision boundary receives raw evidence but does not itself mutate the underlying synthesis.

## Hypothesis

Unknown. The next test asks whether a recipient consequence that the existing extractor *does* turn into an ordinary claim can cross Cognitia's existing research evidence and synthesis path and thereby change the answer state, without a communication-specific interpreter.

## Experiment

Hold a baseline research state constant with two candidate causal observations:

- resource exhaustion caused the service collapse;
- dependency failure caused the service collapse.

Then run two separate recipient consequences through the ordinary `EnvironmentObservation -> OpenEndedResearch -> claim extraction -> genealogy -> OpenResearchResult.augment -> ResearchSynthesisEngine -> AnsweringCore.revise` path:

1. a causal consequence containing a dependency timeout and the service collapse;
2. an unrelated display/dashboard consequence.

The experiment does not tell Cognitia which consequence is relevant, what it means, what state should change, or what communication strategy should be learned.

## Zero-handholding boundary

No expected interpretation, relevance label, preferred communication act, success/failure label, target answer, or learning rule is supplied.

## Result

To be completed from CI output. The artifact is `.ci/communication-consequence-evidence-integration.json`.

## Interpretation boundary

The important distinction is between three boundaries:

1. whether the raw response becomes an extracted claim;
2. whether that claim changes the synthesized evidence state;
3. whether the changed evidence state changes the answer.

The experiment must not collapse these into one result.

## Provenance

- consequence interpretation: `observed` until the actual result is inspected
- evidence integration: `unknown`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`
- independence from handholding: not established by CI success alone

## Next hypothesis

Only after inspecting the actual result. No new communication-specific interpretation layer should be added merely to force a state change.
