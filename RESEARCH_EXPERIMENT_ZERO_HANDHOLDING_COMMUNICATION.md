# Experiment: Zero-Handholding Communication Exposure

## Research question

Does the current communication-facing answering path change its behavior when the same cognitive state is exposed under different interaction objectives and recipient contexts, without being told what communication strategy should be used?

## Method

The experiment reuses the existing `ResearchSynthesis` and `AnsweringCore` on `main`. The cognitive state is held constant. Four interaction contexts are recorded:

- inform / operator
- teach / learner
- decide / decision_maker
- coordinate / operator

The contexts are not converted into an expected act, score, policy rule, or answer template. No communication mechanism is added to make the system pass.

## Handholding boundary

The experiment supplies no:

- expected communication strategy;
- expected act;
- expected recipient adaptation;
- preferred output;
- consequence interpretation;
- learning rule.

The purpose is to expose the current system to a communication demand and observe what it already does.

## Evidence

The CI-generated `.ci/zero-handholding-communication-exposure.json` artifact is the research evidence. CI success only establishes that the experiment executed.

## Interpretation rule

If outputs remain identical, that is an observed capability boundary: the current answering path is not consuming the exposed interaction context. We should not patch that result into adaptation.

If outputs differ, inspect the actual differences before introducing any new communication abstraction.

## Next boundary

Only after this exposure result is inspected should we decide whether the next experiment should introduce an actual interaction consequence. If a consequence is introduced, the system must choose its communication behavior before the consequence is supplied, and the consequence must be observed rather than encoded as the expected outcome.
