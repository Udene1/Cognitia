# Research: communication consequence supported-domain evidence

## Observation

PR #53 exposed a synthesis boundary: generic engineering claims were extracted, but `ResearchSynthesisEngine` discarded them because their inferred domain was `other`. The experiment therefore could not isolate evidence integration.

## Hypothesis

If the existing synthesis domain taxonomy can already recognize the factor vocabulary, then an extracted recipient consequence may be able to cross the ordinary evidence and synthesis path and change the answer state without a communication-specific interpreter. The result may also show no change; the direction is not prescribed.

## Experiment

The domain taxonomy was unchanged. The first run used the word `systemic` in the fixture vocabulary because the experiment was intended to exercise the existing systemic domain. Two raw recipient consequences were then processed through the ordinary evidence path.

## Zero-handholding boundary

Cognitia received raw environment observations. Relevance was not supplied. The experiment observed whatever claim extraction, synthesis, and answer revision actually occurred.

## Result — first run

CI run `35251089061` completed successfully, but the intended supported-domain condition was **not actually established**. The baseline and both augmented cases produced zero synthesis factors and `insufficient_explanatory_structure`.

The reason is visible in the existing implementation: the `systemic` domain bucket does not contain the literal term `systemic`; its configured terms include words such as `internal`, `external`, `institution`, and related phrases. Therefore the fixture's `systemic ...` wording still resolved to domain `other` and was discarded by factorization.

This is an experiment-design failure discovered by the run, not a cognitive result. It is preserved here rather than silently corrected.

The first run therefore establishes only that:

- claim extraction succeeded for both consequence types;
- the current domain taxonomy is lexical and narrower than its domain names suggest;
- the intended evidence-integration experiment remained confounded by factorization.

## Interpretation boundary

No conclusion about communication consequence evidence integration can be drawn from the first run. The next step is to rerun the same experiment using a literal term already present in the existing `systemic` bucket, without changing the Cognitia implementation. That isolates the synthesis boundary rather than repairing it.

## Provenance

- consequence interpretation: `observed`
- claim extraction: `observed`
- supported-domain setup: `failed in first fixture because domain vocabulary was misread`
- evidence integration: `unknown`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`
- independence from handholding: not established by CI success alone

## Next hypothesis

Using an existing lexical term such as `internal` should allow the factorization boundary to be exercised. The next run must determine whether that actually happens; no expected synthesis or answer change is supplied.
