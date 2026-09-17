# Research experiment: experience provenance through epistemic processing

## Question

When retrieved experience changes active cognitive state, can Cognitia preserve its distinction from knowledge, self-model, and other/world-model information while still sending a held-out problem through the existing epistemic operation-selection path?

## Why now

The state-transition boundary audit established that `Experience.state_update` was recorded but had no external consumer. This experiment introduces the smallest explicit transition needed to make the boundary observable.

The transition does not promote experience into knowledge. It preserves a dedicated experience identity and marks the transferred experience as unresolved for epistemic processing. Refuted experience additionally preserves an explicit refutation marker.

## No-handholding rule

The harness supplies the prior experience and its observed outcome because this experiment is specifically about the experience-to-state boundary. It does **not** supply:

- the expected operation;
- the expected information-need classification;
- an expected ranking;
- an expected answer.

The held-out problem is structurally related but not identical to the prior problem.

## Observables

The CI artifact records:

- state before and after experience transfer;
- knowledge, experience, self-model, and other/world-model collections;
- uncertainty introduced by the transfer;
- information-need classification;
- all operation assessments;
- the selected operation.

## Evidence rule

Green CI is only the engineering gate. The generated `.ci/experience-provenance-epistemic-boundary.json` artifact is the research evidence.

## Next boundary

The next reduction in researcher control is to stop supplying the prior experience and its actual outcome. Cognitia should encounter and record the experience through its own interaction loop, after which transfer to a genuinely new problem can be tested.
