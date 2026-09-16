# Differential Research Trajectory Experiment

## Status

Protocol implemented; CI observation pending.

## Research question

When the research question is held constant but the first acquired evidence differs, does Cognitia's subsequent research trajectory change because the evidence changes the information need?

## Hypothesis

For the fixed question `Why did service fail?`, replacing only the first evidence with either resource exhaustion or dependency failure will produce a different second information need and therefore a different second research objective/action.

## Controls

- Same research question in all runs.
- Same adaptive controller and search planner.
- Same number of rounds and acquisition limits.
- Only the first evidence content changes between the two experimental conditions.
- A same-evidence control repeats the resource-exhaustion condition to test trajectory reproducibility.

## Required observations

Each trajectory records:

1. initial evidence;
2. initial action;
3. information need derived from the preceding evidence;
4. source claim/document identifiers for that need;
5. next research objective/action;
6. parent action relationship;
7. decision rationale.

The experiment is not considered informative merely because CI is green. The research observation is the relationship between the changed evidence state and the changed subsequent trajectory.

## Interpretation boundary

Even if the two trajectories diverge, that establishes evidence-conditioned behavior in the implemented controller, not learned cognition by itself. The current controller contains explicit deterministic branches for conflict, claim identity, and evidence acquisition. A later experiment must determine whether trajectory adaptation generalizes across changed questions and evidence states without question-specific routing.

## Next discriminator after this experiment

If differential divergence is observed, run a changed-question/state generalization experiment using the same evidence-to-action mechanism. Compare the observed transition against the controller's explicit routing rules. The purpose is to determine whether the behavior is merely deterministic implementation or evidence of a more general research capability.
