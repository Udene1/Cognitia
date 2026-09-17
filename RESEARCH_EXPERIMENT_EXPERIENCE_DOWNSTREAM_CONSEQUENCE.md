# Experience Downstream Consequence — Research Record

## Question

Can a bound experience with a changed outcome alter a later information-seeking action?

## Protocol

Cognitia receives a training episode, a binding-preserving held-out episode, a binding-rewired control, and a later follow-up problem. The experience is marked **refuted**, so the test is whether that experience can affect what is investigated later rather than merely whether it is considered relevant.

No expected action, hypothesis identifiers, uncertainty labels, or researcher-selected winner are supplied. Candidate order is reversed.

## Important boundary

The experiment intentionally starts with a deterministic experience ledger containing one system-generated experience. This is testing downstream use of an experience record, not yet the full autonomous cycle that discovers and records the experience itself.

## Observed result

Artifact: `experience-downstream-consequence` from workflow run `35231163840`, commit `3d14e72fa74e6e03edff01ce6977082616c8de18`.

- **Held-out transfer:** the refuted experience reached the binding-preserving held-out structure (`relevant_ids: ["system-generated-1"]`).
- **Rewired rejection:** the same experience was rejected by the binding-rewired control (`relevant_ids: []`).
- **Follow-up score change:** no change. With and without the experience, the four candidate scores were identical: `1.0, 0.82, 0.78, 0.74`.
- **Follow-up selected action:** no change. Both conditions selected the same direct-evidence action: `The telescope image did not improve after worker throughput increased.`
- **Held-out scoring consequence:** scores did change on the held-out structure: with experience `0.75, 0.65, 0.63` versus without experience `1.0, 0.9, 0.88`, while the selected action remained the same.
- **Researcher control:** no expected action or hypothesis IDs were supplied.
- **Candidate-order control:** candidate order was reversed.

## Interpretation

The experience-to-structure bridge crossed the transfer boundary and respected the rewired structural control. It therefore did not behave as a simple unconditional attachment to every later state.

However, the refuted experience did **not** change the later information-seeking action. On the follow-up problem it did not even change the candidate scores. On the held-out binding-preserving structure it did change scores, but selection remained unchanged.

The current evidence therefore places the observed boundary **after experience transfer but before downstream behavioral selection** for this refuted experience. The result does not show that refutation can change future investigation choice. It shows that the experience can be structurally retrieved in a held-out case without necessarily changing what Cognitia actually investigates.

The next experiment should therefore not add another abstraction layer merely to force behavioral change. It should isolate why a transferred experience can alter held-out scoring while failing to cross the action-selection boundary, and whether the same boundary persists when the transferred experience is not refuted or when the action margin is intentionally closer.

The experiment does not establish semantic understanding, general learning, or cognition.
