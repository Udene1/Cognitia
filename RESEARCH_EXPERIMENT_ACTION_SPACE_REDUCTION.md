# Action-space reduction research

## Question

What survives when experience is applied across weaker surface similarity, candidate ordering is unhelpful, contradiction arrives later, and evidence can be partial?

## Research position

This is not a final learning architecture. The current `ResearchSearchPlanner` still supplies a researcher-authored vocabulary of search actions, and `ExperienceAwareActionSelector` still consumes those actions. The experiment therefore tests robustness of the existing bridge while explicitly identifying the remaining researcher scaffolding.

## Controls removed

- no expected action is supplied to the evaluator;
- the training action is produced by Cognitia's own planner;
- candidate ordering is reversed;
- the held-out problem uses substantially different surface wording;
- contradiction is introduced as a later epistemic outcome;
- partial evidence is measured separately.

## Evidence required

A CI result is only engineering evidence. The research evidence is the recorded trajectory: candidate actions, ranking scores, relevant experience IDs, selected actions, and changes after contradiction or partial evidence.

## Observed result: action-space-reduction-v1

The experiment artifact from CI run 35091097053 recorded four important observations:

- `action_space_was_researcher_authored = true` — the intermediate vocabulary is still supplied by `ResearchSearchPlanner`;
- `weak_relation_influence = false` — the held-out problem did not retrieve the training experience through the current lexical/state relevance mechanism;
- `late_contradiction_changes_selection = false` — the later contradiction did not alter selection under this setup;
- `partial_evidence_is_distinct = true` — a partial experience was retrieved and contributed a measurable score change.

The trajectory is more informative than the green workflow result. In the training and weakly-related held-out conditions, no prior experience was retrieved. In the partial-evidence condition, `partial-1` was retrieved and changed the ranking score, while the selected action remained the same. This shows that the current bridge can represent and measure partial influence, but the experiment did not demonstrate transfer across the weaker surface relation or revision after a later contradiction.

The late-contradiction observation is especially important: the experiment did not merely fail to produce a different answer; the recorded candidate assessments contained no relevant experience IDs in that condition. Therefore the current mechanism had no opportunity to revise its choice. That is a limitation of the bridge's applicability/relevance representation, not evidence that contradiction itself is ineffective.

## Interpretation boundary

Even a stable behavioral effect does not establish general cognition, learning, or transfer. It establishes only what this explicit mechanism did under these conditions.

## Test-suite observation

The same CI commit exposed three stale unit-test assumptions. One expected an epistemically `REFUTED` experience to have `discrepancy=False`, which conflicts with the corrected epistemic semantics. Two others expected experience to force a different selected query, although the implementation explicitly treats experience as defeasible evidence rather than an unconditional routing rule. Those tests were updated to measure influence through score/relevance/rationale instead of requiring a different action string.

## Next reduction

Remove the planner-authored intermediate action vocabulary. Candidate actions should instead be constructed from the current cognitive state, unresolved hypotheses, uncertainty, observed consequences, and available operations. The evaluator should not prescribe intermediate search facets such as `mechanism causes`, `definition`, or `history`.

The next experiment must preserve the same instrumentation discipline: record the state that generated each candidate, the available operation set, candidate provenance, scores/selection, evidence obtained, and any revision after new evidence. The researcher should specify only the problem/environment, constraints, and discriminator—not the intermediate actions Cognitia is expected to invent.
