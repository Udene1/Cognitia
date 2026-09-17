# Research: communication consequence supported-domain evidence

## Observation

PR #53 exposed a synthesis boundary: generic engineering claims were extracted, but `ResearchSynthesisEngine` discarded them because their inferred domain was `other`. The first run of this experiment then exposed a second fixture mistake: the word `systemic` is not itself a configured term in the existing systemic bucket.

## Hypothesis

If the existing synthesis domain taxonomy can already recognize the factor vocabulary, then an extracted recipient consequence may be able to cross the ordinary evidence and synthesis path and change the answer state without a communication-specific interpreter. The result may also show no change; the direction is not prescribed.

## Experiment

The Cognitia implementation and domain taxonomy were unchanged. After recording the first fixture failure, the experiment used literal terms already present in the existing `systemic` bucket (`internal`). The same baseline research state was then used for two raw recipient consequences:

1. a causal internal dependency-timeout consequence;
2. an unrelated dashboard consequence.

Both consequences passed through `EnvironmentObservation -> OpenEndedResearch -> claim extraction -> genealogy -> OpenResearchResult.augment -> ResearchSynthesisEngine -> AnsweringCore.revise`.

## Zero-handholding boundary

Cognitia received raw environment observations. No relevance label, expected interpretation, expected state change, preferred communication act, success/failure label, target answer, or communication-learning rule was supplied.

## Result

The corrected CI run `35251196481` completed successfully.

The baseline now produced two `systemic` factors:

- `Internal resource exhaustion`
- `Internal dependency failure`

and a candidate multi-factor answer.

### Causal recipient consequence

The consequence was:

> The internal dependency timeout caused the service collapse; CPU remained below its limit during the same interval.

The existing extractor produced one claim with relation `caused`. The ordinary synthesis path added a third factor:

- `The internal dependency timeout`

The answer therefore changed from the two-factor baseline to a three-factor candidate explanation. `revision_changed` was `true` and the new fingerprint differed from the baseline.

### Unrelated recipient consequence

The consequence was:

> The dashboard color changed during the incident, and the display was updated during the outage.

The existing extractor produced one claim with relations `changed` and `was`, but the synthesis path did not turn it into a factor. The factor set remained the two baseline factors and the answer text remained the same as the baseline. `revision_changed` was still `true` because the evidence/genealogy state changed, but the synthesized conclusion did not gain a new factor.

### Differential observation

The controlled comparison showed:

- baseline factor count: `2`
- causal consequence factor count: `3`
- unrelated consequence factor count: `2`
- causal consequence added a factor: `true`
- unrelated consequence added a factor: `false`
- causal consequence changed the answer relative to unrelated consequence: `true`
- both cases started from a supported baseline: `true`

This establishes an important boundary: **once a recipient consequence becomes an ordinary extracted claim that the existing synthesis machinery can factorize, the consequence can change Cognitia's synthesized evidence state and answer without a communication-specific interpreter.**

It does not establish that Cognitia understood the recipient's communicative intent, judged the consequence as relevant, or learned a communication strategy. The causal/unrelated distinction was controlled by the experiment inputs; Cognitia was not told which one mattered.

The result also distinguishes raw-consequence failure from evidence-path capability:

`raw response -> extraction failure` was observed in PR #51;
`raw response -> extraction difference but no revision` was observed in PR #52;
`raw response -> extracted claim -> synthesis change -> answer change` is now observed for the supported-domain causal case.

## Interpretation boundary

The evidence path is capable of carrying at least some recipient consequences into downstream cognitive state. The remaining question is not whether a consequence can ever change state; it can. The harder question is whether Cognitia can discover, from consequences themselves, which aspects of communication caused useful changes and transfer that experience to a new interaction without being told the preferred communication act or outcome.

No communication-learning abstraction should be added merely because this experiment produced a change. The next experiment should remove the explicit causal wording from the recipient consequence while preserving an actual consequence difference, then observe whether Cognitia's existing machinery can discover a useful distinction or simply fail.

## Provenance

- consequence interpretation: `observed`
- claim extraction: `observed`
- evidence integration: `observed for supported-domain causal consequence`
- answer-state change from consequence: `observed`
- communication adaptation: `unknown`
- autonomous communication learning: `unknown`
- independence from handholding: supported by the controlled boundary, not by CI success alone

## Next hypothesis

Can Cognitia extract and use a consequential difference when the recipient response does **not** explicitly state the causal relationship in the sentence itself? That experiment should hold the prior state constant, remove the supplied causal connective, expose only the observed consequence, and let the existing machinery determine what—if anything—changes. No expected interpretation or preferred communication strategy should be supplied.
