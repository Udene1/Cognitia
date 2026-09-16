# Research Experiment: Conditional Operation Choice

## Question

Can Cognitia treat internet search as one available operation rather than a default response, by comparing it with non-search operations from the current cognitive state?

## Why this boundary

The state-action experiment removed the researcher-authored search facets from intermediate action generation. The information-need experiment then introduced an explicit distinction between external evidence, computation, local evidence, sufficient state, and unresolved uncertainty.

That still leaves a stronger hidden assumption: a detector can label a request before Cognitia actually compares possible ways of changing its state.

This experiment moves one step closer to that boundary.

## Experimental mechanism

Several operations are made available at the same time:

- external evidence acquisition (`search`)
- local evidence inspection (`inspect`)
- computation (`compute`)
- reasoning over existing evidence (`reason`)

Each operation has an explicit acquisition cost. The selector records:

- expected state improvement
- cost
- risk
- net value
- state-derived reasons
- every competing assessment
- selected operation

Search is therefore not special in the interface. It is one operation competing with alternatives.

## Important limitation

The current information-need detector and operation selector are deterministic experimental hypotheses. They are not semantic understanding, a learned routing policy, or evidence that Cognitia knows when search is necessary for arbitrary requests.

In particular, the selector currently contains explicit capability-to-need mappings. Those mappings are scaffolding that must eventually be challenged and replaced, not treated as the final cognitive mechanism.

## Evidence standard

A green CI run is not the research result.

The useful artifact is `.ci/operation-choice-research.json`, which records the complete set of competing options and the reasons for the selected operation. Future experiments must inspect observed consequences, not only the selected label.

## Current controlled conditions

1. Freshness requirement: external evidence should have a distinct state-derived advantage.
2. Computation request: computation should compete successfully without external search.
3. Sufficient existing evidence: reasoning should compete successfully without external search.
4. Unresolved uncertainty: multiple acquisition/reasoning options remain visible rather than silently forcing search.

## Next boundary

Do not immediately build a larger router.

Execute the chosen operation and record:

`state -> candidate operations -> expected improvement/cost -> choice -> observed consequence -> state change -> experience -> next choice`

The critical question then becomes whether Cognitia can discover from consequences that an operation was unnecessarily expensive, insufficient, or unexpectedly useful—and revise later choices without being given the answer in advance.

That is the point at which the search question becomes a real cognitive experiment rather than a routing-rule exercise.
