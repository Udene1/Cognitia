# Research: communication consequence differential

## Observation

The independent-consequence experiment routed recipient responses through `EnvironmentObservation` and the existing `DocumentClaimExtractor`. The three controlled responses produced zero extracted claims. The responses were therefore retained as observations but did not become candidate claims through the current extraction boundary.

## Hypothesis

Unknown. The next experiment tests whether changing the semantic content of an unparsed recipient consequence changes anything downstream in the existing cognition path, without introducing a communication-specific interpretation rule.

## Experiment

Hold the same prior `ResearchSynthesis` and `AnsweringCore` state constant. Present two different raw recipient consequences:

1. one containing a concrete timing/counterfactual trace relevant to the unresolved discrimination requirement;
2. one containing unrelated incident information without the discriminating trace.

For each case, run the existing `DocumentClaimExtractor` and `AnsweringCore.revise` exactly as implemented. Do not translate either response into claims, labels, preferred communication acts, state transitions, or learning rules.

## Zero-handholding boundary

Cognitia receives only the raw consequence. The experiment does not provide an expected interpretation, expected revision, relevance label, success/failure label, or communication-learning rule.

## Result

To be completed from CI output. The artifact is `.ci/communication-consequence-differential.json`.

## Interpretation boundary

If the two consequences produce identical extraction and revision behavior, that establishes a current downstream insensitivity to raw semantic content at these boundaries; it does not prove that communication learning is impossible.

If they differ, inspect exactly where and how before adding any learning abstraction.

## Provenance

- consequence interpretation: `observed` until the actual result is inspected
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`
- independence from handholding: not established by CI success alone

## Next hypothesis

Only after the actual differential result is recorded. No communication interpreter should be added merely to make the experiment succeed.
