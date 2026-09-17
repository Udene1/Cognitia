# Experience and Operation Choice

## Research question

> Can a structurally related prior experience interfere with Cognitia's choice of epistemic operation when the new problem requires fresh evidence?

This is the next boundary after the experience downstream-consequence and relative-action experiments. The question is deliberately about **operation choice**, not merely which search/action candidate wins.

The concern is a possible blindspot of the form:

`prior experience -> avoid inspection/search`

when the current state itself still requires evidence acquisition.

## Current evidence entering this experiment

The completed downstream-consequence experiment established that a refuted experience can transfer to a held-out structurally related problem and alter candidate evaluation without determining the selected action. The follow-up evidence-boundary and relative-action experiments showed that the current experience contribution can change absolute candidate scores while preserving their relative ordering because the contribution was uniform across the candidate set.

Therefore the next useful boundary is whether experience reaches the **operation-selection layer** at all.

## Experimental design

For each of three fresh epistemic states:

1. a request with an explicit freshness requirement;
2. an unresolved local-uncertainty problem;
3. a computational problem;

run the same state under:

- no relevant experience;
- a confirmed structurally related experience;
- a refuted structurally related experience.

For every condition record:

- the detected information-need kind and reasons;
- all operation assessments and net values;
- the selected operation;
- the experience-conditioned search/action trajectory from the existing experience bridge;
- relevant experience IDs.

The experiment deliberately does **not** supply an expected operation or expected action. The harness records what the existing mechanisms do.

## Important separation

`ExperienceAwareActionSelector` is evaluated separately from `InformationNeedDetector` and `OperationSelector`.

This matters because a result showing operation-choice invariance can only establish a boundary of the **implemented path** if experience is not actually wired into operation selection. It must not be interpreted as proof that experience can never influence operation choice in a different architecture.

The experiment therefore asks two observable questions:

1. Does experience alter the upstream candidate/action evaluation on these states?
2. Does the operation selector receive a different epistemic state/need or choose a different operation as a consequence?

## Blindspot discriminator

The strongest observation available from this experiment is:

> experience can be active upstream while the current operation-selection mechanism remains governed by the current epistemic state rather than the stored experience.

A changed operation would identify a new interaction boundary requiring further investigation. An unchanged operation would establish that the tested experience path does not currently close the new problem's epistemic state at operation choice.

Neither result establishes general cognition or proves the absence of blindspots elsewhere.

## Anti-handholding constraints

- no expected operation is encoded;
- no expected action is encoded;
- no scenario-specific routing rule is added;
- the existing information-need detector is used unchanged;
- the existing operation selector is used unchanged;
- the existing experience-aware action selector is used unchanged;
- the artifact records the actual trajectory rather than converting the research hypothesis into a test assertion.

## Result status

**Pending execution.**

The CI artifact, not workflow success, is the research result. After execution the artifact must be inspected, the actual result recorded here, and only then should the branch be merged and the next boundary selected.
