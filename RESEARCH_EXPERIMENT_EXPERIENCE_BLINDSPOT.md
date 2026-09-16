# Experience, Generalization, and Blindspots

## Research question

> Does what happened to Cognitia previously change what it does on a genuinely new problem, and does that change remain defeasible when new evidence conflicts with the prior experience?

This is deliberately harder than asking whether a stored experience can be retrieved.

## Why the blindspot matters

Experience is useful only if it can change future behavior without becoming an unquestionable routing rule.

A system that remembers a previous consequence and then repeatedly applies the same response can look like learning while actually becoming less sensitive to new evidence. This creates a blindspot:

`experience → action`

without the required competing path:

`new evidence → challenge experience → update/reject experience → changed action`.

Therefore Cognitia must treat experience as **defeasible evidence**, not permanent truth.

## Required experiment structure

Each experience-conditioned trial must expose four measurements:

1. **Experience-absent baseline** — behavior with the relevant prior experience unavailable.
2. **Experience-present trial** — the same class of new problem with the prior experience available.
3. **Conflict trial** — new evidence contradicts the old consequence or makes its applicability uncertain.
4. **Recovery trial** — after the conflict, present a new problem where the old experience would be misleading if retained unchanged.

The experiment must preserve the raw trajectory for all four conditions.

## Blindspot discriminators

A result is not sufficient merely because experience changes an action.

We need to measure:

- **influence:** does experience change future action?
- **transfer:** does that influence survive a changed surface problem?
- **specificity:** does the influence depend on the relevant state features rather than indiscriminate reuse?
- **defeasibility:** does contradictory new evidence weaken, reject, or supersede the prior experience?
- **recovery:** after being contradicted, can later behavior recover rather than remain anchored?
- **novelty:** can the system choose an action not directly encoded by the prior experience?
- **persistence:** does the change survive beyond the immediate next interaction?

## Less hand-holding

The researcher should specify the protocol and observables, not the answer path.

The next implementation should therefore avoid scenario-specific statements such as:

`if experience X then choose action Y`.

Instead, Cognitia should expose experience candidates to the existing decision process with provenance and applicability information. The decision mechanism must remain responsible for selecting an action.

The experiment harness should generate or select held-out problems from structural properties, then report what Cognitia actually did. It must not encode the expected action for each problem.

As the research progresses, move from:

`researcher specifies scenario → researcher specifies expected action → system executes`

toward:

`researcher specifies question → system constructs state → system selects action → environment supplies consequence → system records experience → system chooses future action`.

Eventually the researcher should specify only the environment, constraints, and discriminator; Cognitia should determine the intermediate path.

## Anti-anchoring principle

Experience records must retain:

- what was observed;
- where it was observed;
- what action preceded it;
- what consequence followed;
- confidence/evidence supporting the record;
- the state features that made it relevant;
- contradictory observations;
- whether later evidence has weakened or superseded it.

An experience must never be treated as universally applicable merely because it produced a successful prior outcome.

## Research boundary

Even if all discriminators pass, this does not by itself establish general cognition. It would establish a stronger form of experience-conditioned, defeasible behavioral adaptation under the tested conditions.

The next question would then be whether the same mechanism can discover useful abstractions across unrelated domains without researcher-authored routing rules.
