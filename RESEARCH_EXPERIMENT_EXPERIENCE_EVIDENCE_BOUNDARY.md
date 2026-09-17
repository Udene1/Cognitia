# Experience Evidence Boundary — Research Record

## Question

Is transferred experience influencing evidence evaluation itself, or merely acting as a blindspot-avoidance signal before action selection?

## Motivation

The previous experiment established that a refuted experience can transfer to a structurally related held-out problem and alter held-out scores, while the selected action remains unchanged. This experiment does not assume why. It changes only the recorded epistemic outcome of the same transferred experience: confirmed versus refuted, with an empty ledger as baseline.

## Protocol

- Keep the training and held-out structural relationship fixed.
- Keep candidate generation and reversed candidate order fixed.
- Run the same held-out problem with no experience, a confirmed experience, and a refuted experience.
- Run the structurally rewired control with both experience outcomes.
- Record all candidate scores, top-two margin, selected action, and retrieved experience IDs.
- Supply no researcher-selected expected action or hypothesis ID.
- Do not add a new cognitive abstraction or force a behavioral change.

## Observed result

CI workflow `experience-evidence-boundary` run `35232238739` completed successfully. The workflow status is only execution evidence; the following is the experiment artifact result.

For the binding-preserving held-out problem:

- **Empty ledger:** scores `1.00, 0.90, 0.88`.
- **Confirmed experience:** scores `1.25, 1.15, 1.13`.
- **Refuted experience:** scores `0.75, 0.65, 0.63`.
- The selected action was unchanged across all three conditions.
- The top-two margin remained `0.10` in all three conditions.
- Confirmed and refuted experiences therefore changed the absolute scores but did not change their ordering or the selected action.
- The binding-preserving held-out case retrieved the corresponding experience; the rewired structural control rejected it for both outcome conditions.
- No researcher-authored expected action or hypothesis ID was supplied.

## Interpretation

This result sharpens the boundary from PR #35.

The transferred experience is not merely present as a retrieval/avoidance flag. Its epistemic outcome directly changes candidate scores: confirmation raises them and refutation lowers them. That is evidence that the experience is participating in evaluation upstream of final selection.

But the effect is currently **action-invariant**. Every candidate receives the same experience contribution in this held-out case, so the relative ordering and selection margin are preserved. The experience is therefore being kept in mind while evidence is evaluated, but it is not yet discriminating among the available investigation actions.

This is consistent with the user's proposed possibility that Cognitia is trying to avoid an experience becoming a blindspot while continuing to focus on evidence. The experiment does not establish that motive; it establishes the observable mechanism: experience outcome changes the absolute evaluation level without changing which candidate wins.

The important next question is now narrower:

> Can experience change the *relative value of competing evidence-seeking actions*, rather than shifting every candidate together?

That should be tested without inventing a new cognitive abstraction. The next experiment should create a structurally valid case in which the existing action-match component differs between candidates, then observe whether confirmed/refuted experience changes the action ordering. If it still shifts all candidates together, that is another boundary. If ordering changes, the behavioral boundary has been crossed.

The experiment does not establish semantic understanding, autonomous learning, generalization, or cognition.
