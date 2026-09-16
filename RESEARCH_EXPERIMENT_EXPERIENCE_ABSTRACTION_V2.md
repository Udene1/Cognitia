# Experience Abstraction v2

## Current research state

The first v2 trajectory already established three important behaviors: representation-invariant causal surfaces can induce a transferable abstraction, the abstraction transfers to the held-out `what caused` surface, and the unrelated control does not match.

The first measurement exposed a more interesting issue: after a contradictory causal experience, the selected abstraction changed from the broad `causal` hypothesis to a narrower hypothesis instead of the original abstraction's support being reduced enough to become non-preferred.

That distinction matters. `contradiction_changes_support` was therefore an insufficient research metric because it compared the newly selected hypothesis rather than the support of the original hypothesis.

The measurement was corrected to record both:

- support of the original abstraction after contradiction;
- identity of the selected abstraction after contradiction.

The next CI trajectory must be inspected using those two separate observations.

## Interpretation boundary

A switch from a broad abstraction to a narrower one is not automatically learning. It may be a useful specialization, or it may be overfitting to incidental surface features. The experiment must distinguish those possibilities before we treat abstraction revision as evidence of learning.
