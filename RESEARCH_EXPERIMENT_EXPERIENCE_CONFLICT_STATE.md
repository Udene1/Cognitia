# Experience conflict-state experiment

## Observation

The completed experience → abstraction → consequence loop showed that confirmed and refuted evidence can cancel the consistency contribution of a shared abstraction and leave action selection at its deterministic baseline.

## Hypothesis

Unknown. The discriminator asked whether contradiction itself becomes an explicit unresolved cognitive state that changes what Cognitia does next.

## Result

CI run `35252071881` succeeded. The experiment produced a shared `causal` abstraction with `positive=1`, `negative=1`, `consistency=0.0`, and explicitly surfaced that hypothesis as contradictory. However, downstream action selection did not change: the contradictory condition selected the same action as absent, confirmed-only, and refuted-only. Candidate scores did differ from the absent condition, but the selected action did not.

## Interpretation

This is a real negative result at the current boundary. Cognitia's existing abstraction machinery can represent contradictory support numerically, but the contradiction is not yet an independent cognitive state that drives a different action. The downstream selector still treats the conflict as ordinary evidence affecting scores and then selects the same deterministic candidate.

Therefore the experiment does **not** establish contradiction-driven information seeking, conflict resolution, or autonomous uncertainty handling.

## Zero-handholding boundary

No expected conflict state, resolution strategy, information need, target action, or state transition was supplied. The artifact records what the existing machinery actually produced.

## Provenance

- contradiction representation: observed as mixed positive/negative support on a shared abstraction
- conflict-state generation: not established
- contradiction-driven information need: not established
- autonomous resolution strategy: not established

## Next hypothesis

If contradiction is not yet actionable, the next experiment should remove the researcher-controlled confirmed/refuted outcome labels from the decision boundary and test whether **independent evidence with incompatible observations** produces a contradiction through the ordinary observation → claim → evidence machinery. This should test whether conflict can emerge from environment evidence rather than from an explicitly constructed epistemic outcome.
