# Experience Relative Action — Research Record

## Question

Can transferred experience change the relative value of competing evidence-seeking actions?

## Motivation

The preceding experiment showed that confirmed and refuted experience changed absolute held-out scores while preserving the selected action and the top-two margin. This experiment tests whether that invariance persists when the recorded experience action is structurally aligned with one generated candidate.

## Protocol

- Keep the held-out problem fixed.
- Generate the candidate actions using the existing deterministic planner.
- Keep that candidate set identical across conditions.
- Record no researcher-selected expected winner.
- Compare empty experience, confirmed experience, and refuted experience.
- Record every candidate score and complete ranking.
- Do not change the selector or introduce a new cognitive abstraction.

The experience action is taken from the first generated candidate only as an existing-system artifact for the experience record; it is not declared the correct action.

## Evidence

CI run `35233854258` completed successfully and produced the `experience-relative-action` artifact. The artifact is the research evidence; workflow success is execution status only.

### Observed result

The experiment generated three candidates with baseline priorities `1.00`, `0.90`, and `0.88`.

- Empty experience: scores remained `1.00`, `0.90`, `0.88`; selected the first candidate.
- Confirmed experience: scores became `1.25`, `1.15`, `1.13`; every candidate referenced the same experience and received the same `+0.25` contribution; selected action remained the first candidate.
- Refuted experience: scores became `0.75`, `0.65`, `0.63`; every candidate referenced the same experience and received the same `-0.25` contribution; selected action remained the first candidate.
- Relative ordering was unchanged in all three conditions.
- No researcher-authored expected action or hypothesis ID was supplied.

The key observation is therefore not merely that action selection stayed unchanged. The existing experience bridge applied the epistemic contribution uniformly across the candidate set, so the experience changed absolute valuation but did not create a candidate-relative difference in this experiment.

## Interpretation

The current evidence establishes another boundary: transferring experience can alter the evaluation level seen by the action selector, but this path did not make the experience action-specific enough to change the relative ordering of competing candidates.

This is consistent with an architecture in which experience is available as evidence upstream of action selection while the current scoring contribution is candidate-invariant. It does **not** establish that Cognitia deliberately avoids experience-driven blindspots, that the mechanism is generally action-invariant, or that experience is irrelevant to behavior in other states.

The next experiment should isolate whether the identity of the action stored inside an experience has any effect on valuation at all. The same problem and candidate set can be held fixed while only the stored experience action is varied across candidates. That tests the action-identity boundary without changing the selector or introducing a new cognitive abstraction.

## Interpretation boundary

This experiment does not establish semantic understanding, autonomous learning, general cognition, or that any selected action is correct.
