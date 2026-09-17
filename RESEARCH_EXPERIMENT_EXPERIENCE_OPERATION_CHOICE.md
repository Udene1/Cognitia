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

## Result — CI run 35235149707

The experiment completed successfully and produced the research artifact. CI success is only the engineering gate; the observations below come from the emitted trajectory artifact/log.

### Observed trajectory

| Current state | Experience condition | Information need | Selected operation | Experience changed selected action? |
|---|---|---|---|---|
| Explicit freshness/current-status request | absent / confirmed / refuted | `external_evidence` | `external-search` | no |
| Unresolved local uncertainty | absent / confirmed / refuted | `unresolved` | `inspect` | no |
| Explicit computation | absent / confirmed / refuted | `computation` | `compute` | no |

The operation trajectory was identical across the three experience conditions for every case. In the unresolved-local case, experience **did** reach the upstream action evaluator: the confirmed experience raised the direct-evidence candidate from `1.00` to `1.25`, while the refuted experience lowered it to `0.75`; the second candidate moved from `0.90` to `1.10` and `0.70` respectively. The selected action nevertheless remained the same.

For the explicit-freshness and computation cases, the stored experience was not structurally relevant to the generated candidates, so their candidate scores remained unchanged.

Most importantly, the operation selector continued to derive its information need from the current state. The freshness case retained `external_evidence` with the explicit-freshness reason and selected `external-search`; the unresolved case retained `unresolved` and selected `inspect`; the computation case retained `computation` and selected `compute`.

## Interpretation

The result is evidence for a sharper boundary than the previous action experiment:

> In the current implemented path, experience can affect upstream candidate evaluation without closing or rewriting the new problem's information need, and the operation selector still acts on the current epistemic state.

Therefore the tested experience path did **not** produce the hypothesized blindspot of preventing inspection/search/compute at the operation-selection layer.

This strengthens the provisional blindspot result, but does not establish general resolution. The experiment did not test every possible route by which experience could enter cognition. In particular, it does not establish what would happen if experience were allowed to alter the information-need state itself, candidate generation, operation-option availability, or accumulated multi-experience evidence.

## Blindspot status after this experiment

**Provisionally resolved across the tested structural-transfer → action-evaluation → operation-selection boundary.**

More precise statement:

> A structurally related prior experience was able to influence upstream candidate evaluation in the tested unresolved case, but did not cause the new problem's information need to be treated as already settled and did not prevent the operation selector from choosing the operation indicated by the current state.

The general blindspot question remains open outside this tested path.

## Next boundary

Do not immediately add an experience-to-operation mechanism. The evidence says the current architecture already preserves the epistemic boundary at operation selection.

The next discriminating experiment should instead attack a different route: **candidate generation**. The question should be whether experience can prevent a necessary investigation candidate from being generated at all, because that would create a blindspot before scoring/selection and is not covered by the present result.

That experiment should again be held-out, compare experience-absent/confirmed/refuted conditions, record the complete generated candidate set before scoring, and avoid encoding an expected candidate.
