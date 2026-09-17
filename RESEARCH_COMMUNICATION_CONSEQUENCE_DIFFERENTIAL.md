# Research: communication consequence differential

## Observation

The independent-consequence experiment routed recipient responses through `EnvironmentObservation` and the existing `DocumentClaimExtractor`. The earlier experiment produced zero extracted claims for all three controlled recipient responses.

## Hypothesis

Unknown. The next experiment tested whether changing the semantic content of an unparsed recipient consequence changes anything downstream in the existing cognition path, without introducing a communication-specific interpretation rule.

## Experiment

The same prior `ResearchSynthesis` and `AnsweringCore` state were held constant. Two different raw recipient consequences were presented:

1. a concrete timing/discriminating trace relevant to the unresolved distinction between resource exhaustion and dependency failure;
2. unrelated incident information without that discriminating trace.

For each case, the existing `DocumentClaimExtractor` and `AnsweringCore.revise` ran exactly as implemented. No response was translated into a communication label, preferred act, state transition, or learning rule.

## Zero-handholding boundary

Cognitia received only the raw consequence. The experiment supplied no expected interpretation, expected revision, relevance label, success/failure label, or communication-learning rule.

## Result

CI run `35250720009` completed successfully and produced `.ci/communication-consequence-differential.json`.

The discriminating-trace response produced **0 extracted claims**. Its revision boundary reported that one item of new evidence was incorporated, but `revision_changed` was `false`; the previous and new fingerprints were identical, the answer was unchanged, and the next action remained to acquire the discriminating trace.

The unrelated dashboard response produced **1 extracted claim**, marked `candidate` with `negative` polarity. Its revision boundary also reported one item of new evidence incorporated, but `revision_changed` was `false`; the previous and new fingerprints were identical, the answer was unchanged, and the next action was unchanged.

Therefore:

- `claim_count_equal`: `false`
- `revision_changed_equal`: `true`
- `fingerprints_equal`: `true`
- `answers_equal`: `true`

The current extraction boundary is therefore sensitive to the semantic form of the raw consequence, but that difference does not propagate into a cognitive-state revision in the tested path.

An especially important observation is that the consequence containing the explicitly discriminating trace was not extracted as a claim, while the unrelated response was. This is a parser/extraction boundary result, not evidence that Cognitia understood or rejected the trace.

## Interpretation boundary

This experiment establishes that raw recipient-consequence content can produce different extraction behavior without producing different `AnsweringCore` revision behavior. It does **not** establish communication learning, semantic understanding, relevance assessment, or an inability to learn from consequences.

The unchanged fingerprints also confirm that the current `AnsweringCore.revise` path does not mutate the underlying `ResearchSynthesis` merely because raw consequence text is passed as `new_evidence`.

The result should not be repaired by adding a communication interpreter yet. The next research question should be derived from this observed boundary rather than from a desired outcome.

## Provenance

- consequence interpretation: `observed`
- extraction sensitivity to consequence content: `observed`
- downstream cognitive-state revision from raw consequence: `not observed`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`
- independence from handholding: supported only by the controlled experiment boundary, not by CI success alone

## Next hypothesis

The next experiment should determine whether a consequence that the existing extractor *does* turn into a claim can cross the same revision boundary when that claim is supplied as evidence through the ordinary evidence path, without telling Cognitia whether the claim should matter or what state change it should produce. The experiment should distinguish extraction failure from downstream evidence-integration failure before any new communication-specific abstraction is introduced.
