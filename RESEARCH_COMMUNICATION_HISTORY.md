# Communication Research History

## Purpose

This document preserves the evidence trail by which Cognitia's communication research direction was reached. It records observations, hypotheses, experiments, results, and the reasoning for subsequent changes. It is intentionally historical: later architecture must not be written backward as though it was known in advance.

---

## 1. Observation that started the investigation

Cognitia's earlier Roman Empire answer exposed a weakness in answer behavior. The problem was not treated simply as poor wording.

The observed answer mixed candidate contributing factors, competing explanations, evidence, uncertainty, and unresolved discrimination requirements without a sufficiently controlled communicative structure. In particular, it did not clearly separate what the system had evidence for, what remained a competing explanation, what evidence would distinguish alternatives, and what the system was actually committing itself to.

This produced the research hypothesis that Cognitia could possess useful problem-solving and epistemic machinery while lacking an explicit capability for deciding how to act communicatively on that state.

The resulting question became:

> Can communication be treated as a cognitive action-selection problem rather than as a prose-generation problem?

---

## 2. Methodological decision: no LLM

Before implementing the experiment, the research method was constrained so that an LLM would not perform the very capability being measured.

For the foreseeable research horizon, Cognitia does not use an LLM for cognition, communicative-act selection, epistemic assignment, experiment evaluation, training-label manufacture from surface answers, or silent repair of failed communicative decisions.

The early experiments therefore use deterministic, inspectable mechanisms. This exposes capabilities for measurement; it is not evidence that deterministic mechanisms are the final architecture.

---

## 3. Experiment 1: objective-conditioned act selection

The first controlled experiment held the underlying cognitive state and recipient constant while changing communicative objective.

The fixed state contained H1 resource exhaustion with strong evidence, H2 dependency failure with weak evidence, H3 configuration error with no evidence, no established root cause, and unresolved discriminating evidence.

The observed mappings were:

| Objective | Selected act |
|---|---|
| Inform | Report current state |
| Investigate | Propose discriminating test |
| Decision support | Support decision under uncertainty |
| Teach | Explain uncertainty |

Additional tests covered ambiguous interaction, insufficient capability, and rejection of candidate-to-established-fact promotion.

### CI result — 2026-09-16

PR #8 (`Begin deterministic communicative cognition experiment`) was exercised by run **35056983672**. The important result was behavioral: controlled objective changes produced different structured communicative decisions while epistemic-preservation tests rejected unsupported upgrades. The cognitive-transfer job also recovered durable state across the runner boundary and continued the existing transfer, discovery, evidence, language, and answer-core sequence.

The result established a controlled implementation capability, not learned communication.

---

## 4. Experiment 2: recipient/context variation

Experiment 2 held the unresolved cognitive state and `INFORM` objective constant while varying recipient role.

The tested behavior was:

```text
OPERATOR + INFORM
    → REPORT_CURRENT_STATE

DECISION_MAKER + INFORM
    → SUPPORT_DECISION_UNDER_UNCERTAINTY

LEARNER + INFORM
    → EXPLAIN_UNCERTAINTY
```

### CI result — 2026-09-16

PR #9 (`Experiment 2: recipient-context-conditioned communication`) was exercised by run **35058177100**.

The `test` job collected **195 tests** and the communication module executed **8 tests**. The full suite ended with:

```text
195 passed, 1 warning in 0.97s
```

The warning was an existing `PytestCollectionWarning` for `TestResult` in `cognitia/learning/scientific.py`.

### What Cognitia did

The significant observation was not the word `passed`. With cognitive state and objective held fixed, changing recipient role caused Cognitia to change the **structured communicative action**. The same state identity, uncertainty, evidence relationships, and verification requirement remained present; recipient change did not promote an unresolved hypothesis to an established fact.

The cognitive-transfer job also restored prior durable cognitive state and continued through its existing transfer, persistence, discovery, evidence, language, and answer-construction stages. Thus the new communication behavior coexisted with the existing cognitive-state machinery in the same CI run.

The evidence boundary remained narrow: this demonstrated explicit recipient-conditioned action selection, not learned recipient modeling or general audience adaptation.

---

## 5. Experiment 3: representation-preserving communication

Experiment 3 follows because an action-selection layer is not enough if changing the representation used to communicate can silently change the epistemic content.

The controlled question is:

> Given one selected communicative act, can Cognitia express that act through different representations without changing claims, evidence, uncertainty, epistemic status, or verification requirements?

The implementation introduces `CommunicationProjection` and three explicit representations:

- `STRUCTURED`;
- `CONCISE`;
- `EXPLANATORY`.

The representation layer does not choose a new communicative act. It receives an already-selected decision and carries its semantic contract into a different payload organization.

A deterministic `assert_projection_preservation` check compares the projection against the original decision for:

- selected act;
- claim identities;
- omitted claim identities;
- epistemic status;
- evidence identities;
- uncertainty;
- verification requirement.

No LLM is involved in projection or preservation evaluation.

### Current implementation evidence

The tests now exercise all three representations from the same unresolved state and selected `REPORT_CURRENT_STATE` act. They require each projection to retain the same act, claim `H1`, evidence `E1`, uncertainty, and required verification. A separate explanatory projection test confirms that the projection cannot invent an `established` status.

CI evidence for Experiment 3 is intentionally **pending**. The implementation result must not be recorded as a successful experiment until CI observes the behavior.

### Research boundary

This experiment does not yet establish arbitrary natural-language semantic equivalence. It establishes a testable separation between communicative action and representation, with an explicit invariant that can fail visibly.

If CI validates the invariant, the next discriminating step is to introduce observable communication consequences. Only then should we test whether experience can modify communicative policy rather than merely executing developer-authored mappings.

---

## 6. Provenance rule

Every future communication milestone must preserve:

1. the observation that motivated the hypothesis;
2. the hypothesis before the result;
3. the controlled experiment;
4. the exact CI/reproduction result that matters;
5. **how Cognitia behaved during the experiment**, not only whether CI passed or failed;
6. failures as well as successes;
7. what the result does and does not establish;
8. the hypothesis changed by the result; and
9. why the next experiment follows from the evidence.

This history is part of Cognitia's research evidence, not merely project documentation.
