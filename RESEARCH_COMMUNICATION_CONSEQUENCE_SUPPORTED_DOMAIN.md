# Research: communication consequence supported-domain evidence

## Observation

PR #53 exposed a synthesis boundary: generic engineering claims were extracted, but `ResearchSynthesisEngine` discarded them because their inferred domain was `other`. The experiment therefore could not isolate evidence integration.

## Hypothesis

If the existing synthesis domain taxonomy can already recognize the factor vocabulary, then an extracted recipient consequence may be able to cross the ordinary evidence and synthesis path and change the answer state without a communication-specific interpreter. The result may also show no change; the direction is not prescribed.

## Experiment

The domain taxonomy is unchanged. A baseline research state uses existing `systemic` vocabulary. Two raw recipient consequences are then processed through the ordinary evidence path:

1. a causal dependency-timeout consequence that also uses existing `systemic` vocabulary;
2. an unrelated dashboard consequence.

The same baseline state is used for both. No consequence is labeled as relevant, and no expected interpretation, state transition, answer, or communication-learning rule is supplied.

## Zero-handholding boundary

Cognitia receives raw environment observations. Relevance is not supplied. The experiment observes whatever claim extraction, synthesis, and answer revision actually occur.

## Result

To be completed from CI output. The artifact is `.ci/communication-consequence-supported-domain.json`.

## Interpretation boundary

The experiment is only useful if the baseline actually produces non-`other` factors. If it does not, the experiment remains confounded by synthesis factorization and that failure must be recorded rather than repaired here.

## Provenance

- consequence interpretation: `observed` until the actual result is inspected
- evidence integration: `unknown`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`
- independence from handholding: not established by CI success alone

## Next hypothesis

Derive only from the actual result. Do not add a communication-specific interpreter merely to obtain an answer change.
