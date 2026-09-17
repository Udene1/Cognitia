# Experience Downstream Consequence — Research Record

## Question

Can a bound experience with a changed outcome alter a later information-seeking action?

## Protocol

Cognitia receives a training episode, a binding-preserving held-out episode, a binding-rewired control, and a later follow-up problem. The experience is marked **refuted**, so the test is whether that experience can affect what is investigated later rather than merely whether it is considered relevant.

No expected action, hypothesis identifiers, uncertainty labels, or researcher-selected winner are supplied. Candidate order is reversed.

## Important boundary

The experiment intentionally starts with a deterministic experience ledger containing one system-generated experience. This is testing downstream use of an experience record, not yet the full autonomous cycle that discovers and records the experience itself.

## Expected observation classes

We do not encode a desired winner. The artifact records:

- whether the experience reaches the held-out state;
- whether the rewired control rejects it;
- whether the later action changes relative to the same problem without experience;
- whether scores change even when selection does not;
- which experience IDs are attached to the selected decision.

## Interpretation

A changed score without a changed action would mean experience has reached the selector but has not crossed the behavioral decision boundary. A changed later action would justify investigating the mechanism that produced that change. Failure to transfer would identify the next representation or state-lineage boundary.

The experiment does not establish semantic understanding, general learning, or cognition.
