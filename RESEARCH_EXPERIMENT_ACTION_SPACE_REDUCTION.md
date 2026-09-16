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

## Interpretation boundary

Even a stable behavioral effect does not establish general cognition, learning, or transfer. It establishes only what this explicit mechanism did under these conditions.

## Next reduction

Remove the planner-authored intermediate action vocabulary. Candidate actions should instead be constructed from the current cognitive state, unresolved hypotheses, uncertainty, observed consequences, and available operations. The experiment should then test whether Cognitia can generate an intermediate action that was not supplied as a researcher-authored facet.
