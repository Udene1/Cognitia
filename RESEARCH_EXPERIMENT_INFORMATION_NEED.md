# Research Experiment: Conditional External Information Need

## Question

Can Cognitia treat internet search as one available operation rather than the default response to every request?

## Why this boundary matters

The state-to-action experiment now removes researcher-authored search facets. The next failure mode would be replacing that hidden hand-holding with a hidden assumption that information-seeking means web search.

A capable system should eventually distinguish at least:

- requests answerable from current state/knowledge;
- requests requiring computation or transformation;
- requests requiring local evidence or inspection;
- requests where external evidence is necessary because freshness or missing evidence matters;
- requests where uncertainty remains and the system must decide what information would actually reduce it.

We are not claiming Cognitia can make these distinctions generally yet.

## Experimental control

The first experiment uses an explicit deterministic detector. This is intentionally modest: it makes the decision boundary visible so that later experiments can replace it without confusing an implementation rule with learned cognition.

The evaluator supplies states only. No expected action is supplied.

## Conditions

1. A request with an explicit freshness requirement.
2. A computation request.
3. A state that already contains sufficient evidence for the simple task.
4. A state with unresolved uncertainty.

The artifact records the detected information-need kind, reasons, and confidence.

## Interpretation

A green CI run is not the finding.

The research evidence is the recorded state-to-need trajectory. In particular, we need to know whether Cognitia is actually conditioning the operation choice on the current state, rather than simply calling search by default.

Even if this detector behaves as designed, it establishes only this explicit mechanism. It does not establish semantic understanding or general routing competence.

## Next reduction

The lexical detector should not become a permanent rulebook. The next experiment should make the cost and consequence of information acquisition observable: an external search should be one possible operation, and Cognitia should have to justify it by expected state improvement relative to alternatives such as computation, inspection, recall, or reasoning from existing evidence.

The eventual research target is not `never search` or `always search`. It is a system that can determine, from its current state and available operations, whether external information is warranted—and can revise that decision after observing what happened.
