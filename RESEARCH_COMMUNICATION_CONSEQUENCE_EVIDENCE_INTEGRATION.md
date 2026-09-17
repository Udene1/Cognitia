# Research: communication consequence evidence integration

## Observation

PR #52 showed that raw recipient-consequence content can change `DocumentClaimExtractor` output, but neither tested consequence changed the `AnsweringCore` fingerprint. The current revision boundary receives raw evidence but does not itself mutate the underlying synthesis.

## Hypothesis

Unknown. The next test asked whether a recipient consequence that the existing extractor *does* turn into an ordinary claim can cross Cognitia's existing research evidence and synthesis path and thereby change the answer state, without a communication-specific interpreter.

## Experiment

The same baseline research state was held constant. Two baseline causal observations were supplied as raw environment documents:

- resource exhaustion caused the service collapse;
- dependency failure caused the service collapse.

Two separate recipient consequences then passed through the ordinary `EnvironmentObservation -> OpenEndedResearch -> claim extraction -> genealogy -> OpenResearchResult.augment -> ResearchSynthesisEngine -> AnsweringCore.revise` path:

1. a causal consequence containing a dependency timeout and the service collapse;
2. an unrelated display/dashboard consequence.

No consequence was labeled as relevant, and no expected state change or communication-learning rule was supplied.

## Zero-handholding boundary

No expected interpretation, relevance label, preferred communication act, success/failure label, target answer, or learning rule was supplied.

## Result

CI run `35250953766` completed the experiment successfully and produced `.ci/communication-consequence-evidence-integration.json`.

The existing extractor produced one claim for each consequence. The causal consequence contained a `caused` relation; the unrelated consequence contained `changed`/`was` relations. However, the existing `ResearchSynthesisEngine` produced **zero factors for the baseline and for both augmented cases**. Its factorization rejects factors whose domain resolves to `other`, and the generic engineering vocabulary in these fixtures did not map to one of its existing domain buckets.

As a result, both cases produced the same insufficient answer state:

> I cannot currently establish a reliable answer to Why did service X fail? from the available evidence. My best current conclusion is that the evidence is insufficient.

Both cases changed the answer fingerprint relative to the baseline, but both changes were caused by the augmented evidence/genealogy state rather than by a changed synthesized conclusion. The causal and unrelated cases produced the same new fingerprint and the same answer.

Therefore the experiment did **not** isolate communication-consequence evidence integration as intended. It exposed a prior boundary: the current synthesis engine cannot construct factors from these generic engineering claims because their inferred domain is `other` and such factors are rejected.

This is a genuine research/implementation observation, not a reason to patch the taxonomy merely to make the communication experiment succeed.

## Interpretation boundary

The experiment establishes that claim extraction itself is functioning for both response types, but the synthesis stage can discard both claims before they become factors when the inferred domain is unsupported. It therefore does not establish whether a semantically relevant recipient consequence would change a properly synthesized cognitive state.

The unchanged answer across the two cases cannot be interpreted as downstream insensitivity yet, because the synthesis layer had already collapsed both cases into an insufficient structure.

The correct next experiment is therefore to isolate the synthesis boundary using claims whose domain is already represented by the existing taxonomy, without changing the taxonomy or telling Cognitia which response is relevant. Only after a baseline can actually form factors should we test whether different extracted recipient consequences alter the synthesized state and answer.

## Provenance

- consequence interpretation: `observed`
- claim extraction: `observed`
- synthesis factorization for generic engineering claims: `failed at existing domain boundary`
- evidence integration: `not established`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`
- independence from handholding: supported only by the controlled experiment boundary, not by CI success alone

## Next hypothesis

The next experiment should hold the same communication boundary constant but use raw consequences whose extracted factor vocabulary already falls within Cognitia's existing domain taxonomy. This is not a fix to the synthesis engine; it is a boundary-isolation experiment to determine whether the evidence path can change synthesis once factorization is actually possible. No communication interpreter should be introduced yet.
