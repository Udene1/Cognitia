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

## Actual result

CI run `35248225402` completed successfully. The research artifact reported `distinct_communication_outputs: 1` across all four contexts.

The answer content, reasoning, evidence, uncertainty, limitations, verification actions, and recorded epistemic fields were identical. Only the externally recorded context labels differed.

Therefore the current `AnsweringCore` did not consume objective or recipient context in this exposure. This is a measured capability boundary, not evidence that context-conditioned communication exists.

## Evidence

The CI-generated `.ci/zero-handholding-communication-exposure.json` artifact is the research evidence. CI success only establishes that the experiment executed.

## Interpretation

The result does not justify adding a hard-coded objective-to-act or recipient-to-style mapping. We have established that the current answering path can preserve epistemic structure, but its communication behavior is presently invariant to the interaction context exposed here.

The next experiment should therefore introduce an actual interaction consequence only after Cognitia has selected its communication behavior. The consequence should be observed rather than encoded as a desired outcome. The experiment should then test whether Cognitia can connect that consequence back to the communication decision.

## Next boundary

Do not patch this experiment into context adaptation. Build the smallest real consequence boundary and let the existing system fail if it cannot select, execute, or learn from communication.
