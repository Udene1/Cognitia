# Communication Research History

## Purpose

This document preserves the evidence trail by which Cognitia's communication research direction was reached. It records observations, hypotheses, experiments, results, and the reasoning for subsequent changes. It is intentionally historical: later architecture must not be written backward as though it was known in advance.

---

## 1. Observation that started the investigation

Cognitia's earlier Roman Empire answer exposed a weakness in answer behavior. The problem was not treated simply as poor wording.

The observed answer mixed candidate contributing factors, competing explanations, evidence, uncertainty, and unresolved discrimination requirements without a sufficiently controlled communicative structure. In particular, it did not clearly separate:

- what the system had evidence for;
- what remained a competing explanation;
- what evidence would distinguish the alternatives; and
- what the system was actually committing itself to.

This produced the research hypothesis that Cognitia could possess useful problem-solving and epistemic machinery while lacking an explicit capability for deciding how to act communicatively on that state.

The resulting question became:

> Can communication be treated as a cognitive action-selection problem rather than as a prose-generation problem?

This observation led to `RESEARCH_COMMUNICATIVE_COGNITION.md` and then to the controlled Experiment 1.

---

## 2. Methodological decision: no LLM

Before implementing the experiment, the research method was constrained so that an LLM would not perform the very capability being measured.

For the foreseeable research horizon, Cognitia does not use an LLM for:

- cognition;
- communicative-act selection;
- epistemic assignment;
- experiment evaluation;
- training-label manufacture from surface answers; or
- silent repair of failed communicative decisions.

The reason is experimental identifiability. A fluent language model could conceal whether Cognitia itself learned what it knows, what the interaction is trying to accomplish, which action is warranted, and whether epistemic status was preserved.

The early experiment therefore uses deterministic, inspectable mechanisms. This is not evidence that a deterministic mechanism is the final architecture. It is a way to expose the capability so that future experiments can determine what should replace it, if anything.

---

## 3. Experiment 1 implementation

The first controlled experiment holds the underlying cognitive state constant and changes only the communicative objective.

The fixed state contains:

- H1: resource exhaustion — strong evidence;
- H2: dependency failure — weak evidence;
- H3: configuration error — no evidence;
- no established root cause;
- unresolved discriminating evidence.

The recipient is held constant as an operator.

The tested objectives are:

| Objective | Selected act |
|---|---|
| Inform | Report current state |
| Investigate | Propose discriminating test |
| Decision support | Support decision under uncertainty |
| Teach | Explain uncertainty |

Additional tests cover ambiguous interaction and insufficient capability.

The implementation records the act separately from any surface representation and includes an epistemic-preservation check.

---

## 4. CI result — 2026-09-16

PR #8 (`Begin deterministic communicative cognition experiment`) was exercised by GitHub Actions run **35056983672**.

The important record is not merely that CI returned `success`. The run shows how Cognitia behaved across the test boundary:

### 4.1 Unit-test behavior

The `test` job:

1. checked out the experiment branch;
2. installed the repository;
3. executed the unit-test suite;
4. completed without a test failure.

The communication-specific suite exercised the new behavior rather than only importing the new types. It verified:

- the same cognitive state + `INFORM` selected `REPORT_CURRENT_STATE`;
- the same state + `INVESTIGATE` selected `PROPOSE_DISCRIMINATING_TEST`;
- the same state + `DECISION_SUPPORT` selected `SUPPORT_DECISION_UNDER_UNCERTAINTY`;
- the same state + `TEACH` selected `EXPLAIN_UNCERTAINTY`;
- ambiguous interaction selected `REQUEST_CLARIFICATION`;
- insufficient capability produced `REPORT_LIMITATION_WITH_PARTIAL_RESULT` and retained a verification requirement;
- candidate-to-established-fact promotion was rejected by epistemic-preservation logic.

So Cognitia did not merely "pass the test": under controlled input changes, it produced different structured communicative decisions while keeping the underlying epistemic state constrained.

### 4.2 Cross-run cognitive behavior

The `cognitive-transfer` job restored **three SQLite cognitive databases** from the durable `cognitia-state` branch and reported:

```text
CI_STATE_CROSS_RUN_RECOVERY_SUCCESS: 1 prior runs recovered
```

After recovery, Cognitia continued through its existing transfer and research-control sequence rather than starting from an empty cognitive state. The run completed the following stages:

- learned from executable source;
- transferred code-derived structure into a new process;
- compared independently written implementations;
- exercised multi-language and representation-neutral abstractions;
- recovered durable cognitive state and used it in a new process;
- identified explanatory gaps and constructed/discriminated hypothesis spaces;
- exercised discovery, evidence convergence, and discriminating-experiment reasoning;
- persisted validated knowledge;
- routed research actions using knowledge/evidence;
- extracted and matched structured claims;
- exercised evidence-driven research action control, decision utility, genealogy, and multi-factor synthesis;
- exercised structured/semantic language representation;
- diagnosed answer-construction state;
- exercised answer construction, epistemic boundaries, and revision.

The answer-core diagnostics artifact was also uploaded successfully.

This matters because the communication experiment did not run in isolation from Cognitia's existing state machinery: the CI execution demonstrated that the existing persistence/transfer path remained operational while the new communication capability was present.

### 4.3 What CI actually demonstrated

The run gives us three different kinds of evidence that should not be collapsed into one word:

**Behavioral evidence**

The communication tests observed objective-dependent act selection and rejection of epistemically invalid transformations.

**Persistence/continuity evidence**

Cognitia recovered prior durable state across the CI runner boundary and continued executing cognitive operations.

**Regression evidence**

The existing cognitive-transfer sequence, including persistence, discovery, evidence reasoning, language, and answer-core stages, completed successfully in the same run.

None of these is evidence that communication was learned.

### Evidence boundary

The CI run establishes that the current explicit mechanism can execute the tested communication distinction and coexist with the current cognitive-transfer path.

It does **not** establish:

- learning from communication consequences;
- recipient modeling;
- audience adaptation;
- unrestricted natural-language communication;
- broad generalization beyond the controlled state;
- discovery of communicative acts rather than use of predefined acts; or
- that the current deterministic selector is cognitively adequate.

The result is therefore recorded as a **controlled implementation result with behavioral, persistence, and regression evidence — not a learning claim**.

---

## 5. What the result changes

The first experiment provides evidence for a separation that was previously only a hypothesis:

```text
underlying cognitive state
        ↓
communicative objective
        ↓
communicative act
```

can be represented and tested independently of prose generation.

It also provides a concrete invariant:

> Communication may reorganize or select what is communicated, but it must not increase epistemic warrant.

However, the current selector is explicitly hand-specified. Therefore the next research question is not "how do we add more acts?" It is:

> Can Cognitia learn a communicative policy from observed interaction consequences, rather than having the appropriate mapping permanently specified by the developer?

Before that, the controlled experiment should be strengthened enough to expose failures in the current explicit mechanism rather than merely expanding its taxonomy.

---

## 6. Evidence-driven next research direction

The next experiment should vary **recipient/context while holding the cognitive state and communicative objective controlled**.

The question is:

> Does Cognitia change the communicative action appropriately when the interaction context changes, without changing the underlying epistemic commitments?

The progression is:

```text
fixed state + objective
        ↓
controlled act selection                [Experiment 1]
        ↓
recipient/context variation             [Experiment 2]
        ↓
surface representation without drift
        ↓
observed recipient/environment outcome
        ↓
communication experience
        ↓
policy/model revision
        ↓
held-out interaction
        ↓
transfer and validation
```

The crucial distinction remains:

```text
developer specifies behavior
        ≠
Cognitia learns behavior
```

A future learned policy should therefore be judged by its ability to change appropriately after experience and transfer that change beyond the exact interaction from which it learned.

---

## 7. Provenance rule for future work

Every future communication milestone should preserve:

1. the observation that motivated the hypothesis;
2. the hypothesis as it existed before the result;
3. the controlled experiment;
4. the exact CI/reproduction result that matters;
5. **how Cognitia behaved during the experiment**, not only whether CI passed or failed;
6. failures as well as successes;
7. what the result does and does not establish;
8. the hypothesis changed by the result; and
9. why the next experiment follows from the evidence.

This history is part of Cognitia's research evidence, not merely project documentation.
