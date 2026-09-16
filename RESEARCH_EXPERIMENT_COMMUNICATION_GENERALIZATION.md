# Experiment 4B: Communication Experience Generalization

## Status

Experimental implementation in progress. This document defines the next research boundary after Experiment 4.

## Research question

> Can a communication consequence experienced on one cognitive state change a later communicative decision for a structurally related but non-identical cognitive state, while preserving the later state's epistemic commitments?

The question is intentionally stronger than repeating Experiment 4 on the same state. A useful learning mechanism must show that experience is represented at a level that can apply beyond the exact state that produced it.

## Hypothesis

**H4B-transfer:** communication experience can revise an inspectable policy keyed to interaction structure rather than exact cognitive-state identity, allowing experience from one unresolved case to influence a structurally related held-out case.

A secondary boundary hypothesis is:

**H4B-boundary:** experience should not automatically transfer across an unrelated communicative objective when objective is part of the interaction structure.

## Experimental design

### Training interaction A

The training state contains two unresolved hypotheses with different evidence strengths. The objective is `INFORM` and recipient role is `OPERATOR`.

The policy receives two controlled consequences:

- `REPORT_CURRENT_STATE` receives a negative signal (`-1.0`);
- `EXPLAIN_UNCERTAINTY` receives a positive signal (`+1.0`).

### Held-out interaction B

The held-out state has different state identity, question, hypothesis identities, evidence identities, and domain wording, but preserves the same structural communication context:

- unresolved cognitive state;
- `INFORM` objective;
- `OPERATOR` recipient role;
- competing supported/weak hypotheses;
- verification remains required.

The policy must be evaluated on B without recording any consequence from B before the decision.

### Unrelated control C

A second held-out evaluation uses a different objective (`INVESTIGATE`) while retaining an unresolved state. Its baseline act is `PROPOSE_DISCRIMINATING_TEST`.

Experience learned under `INFORM + OPERATOR` must not globally force `EXPLAIN_UNCERTAINTY` in this unrelated objective context.

### Representation shift

After adaptation on held-out B, the selected act is projected through `COMPACT_REFERENCED`.

The projection must preserve the held-out state's claims, evidence identity, uncertainty, epistemic status, and verification requirement. Evidence may be compacted only through the already-established lossless-reference boundary.

## Anti-memorization requirement

The policy must not learn a mapping of the form:

```text
exact_state_id -> act
```

Instead, policy state is keyed by interaction structure:

```text
objective + recipient_role + candidate_act
```

The exact cognitive state ID therefore does not appear in the policy key.

This is still a deliberately small deterministic learner. The structural key is an experimental instrument that makes the generalization hypothesis measurable; it must not be treated as evidence that Cognitia has already discovered the correct abstraction autonomously.

## Controls

1. **Fresh-policy control:** B must select its original baseline act before any training experience is recorded.
2. **Held-out identity control:** A and B must have different state IDs, hypothesis IDs, evidence IDs, and questions.
3. **Unrelated-objective control:** experience from A must not alter the selected act for C's `INVESTIGATE` objective.
4. **Epistemic control:** adaptation on B may change the selected communicative act but must not change claim identity, evidence identity, uncertainty, epistemic status, or verification requirement.
5. **Representation control:** the adapted B decision must remain valid after projection to `COMPACT_REFERENCED` and its evidence must remain losslessly recoverable.

## Evidence that would support H4B

A result supports the hypothesis if all of the following are observed:

- A's experience changes inspectable policy state;
- fresh B remains at its baseline act;
- the adapted policy changes B's act after A's experience;
- A and B have different cognitive identities and content;
- the policy revision contains no exact B state identity;
- C does not inherit the A preference across an unrelated objective;
- B's epistemic commitments remain unchanged;
- the adapted B decision survives the representation shift with recoverable evidence.

## Evidence that would weaken or falsify H4B

The hypothesis is weakened if adaptation only works when the exact state is reused, or if changing state identity/content prevents transfer.

It is weakened if the policy changes every communication context regardless of objective or recipient.

It is weakened if the apparent transfer is caused by an explicit state-specific rule or a hidden lookup rather than a reusable policy representation.

It is also weakened if adaptation changes epistemic commitments, invents evidence, drops uncertainty, or changes verification requirements.

## Interpretation boundary

Even a successful result would establish only **controlled structural transfer of a communication policy**. It would not establish general learned communication, natural-language learning, autonomous discovery of communication abstractions, or human-level social reasoning.

A successful result would justify the next question: whether the structural representation itself can be learned from experience rather than supplied as an experimental feature key.

## Decision record

Experiment 4 demonstrated the complete local loop:

```text
experience -> policy revision -> future decision
```

Experiment 4B deliberately moves one step outward:

```text
experience on A
    -> policy revision
    -> decision on structurally related B
    -> representation shift
    -> epistemic-preservation check
```

The broader Cognitia roadmap remains intact. This experiment tests one specific missing capability: whether interaction experience can influence a future case without requiring the exact prior cognitive state to recur.
