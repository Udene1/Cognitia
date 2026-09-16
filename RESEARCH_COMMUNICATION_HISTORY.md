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

PR #8 (`Begin deterministic communicative cognition experiment`) was tested in GitHub Actions run **35056983672**.

The `test` job completed successfully, including the unit-test suite. The `cognitive-transfer` job also completed successfully. The runner restored three SQLite cognitive databases from the durable `cognitia-state` branch and reported:

```text
CI_STATE_CROSS_RUN_RECOVERY_SUCCESS: 1 prior runs recovered
```

The cognitive-transfer run then completed all existing transfer, persistence, discovery, language, and answer-core steps successfully. The answer-core diagnostics artifact was uploaded successfully.

Most importantly for this communication experiment, the PR added `tests/test_communicative_cognition.py`, and the CI unit-test job passed. The tests establish the following narrow behaviors:

1. The same cognitive state produced four different communicative acts when the objective changed.
2. Changing the objective did not manufacture an established hypothesis.
3. Ambiguous recipient/objective state selected clarification rather than an arbitrary claim.
4. A capability limitation still permitted a partial-result communicative act with verification required.
5. An attempted candidate-to-established-fact upgrade was rejected by the epistemic-preservation check.

The implementation itself is deterministic and contains no LLM dependency.

### Evidence boundary

These results establish that the current explicit mechanism can represent and execute the tested distinction. They do **not** establish that Cognitia has learned communication.

In particular, the experiment does not yet demonstrate:

- learning from communication consequences;
- audience adaptation;
- unrestricted natural-language communication;
- broad generalization beyond the controlled state;
- discovery of communicative acts rather than use of predefined acts; or
- that the current deterministic selector is cognitively adequate.

The result is therefore recorded as a **controlled implementation success, not a learning claim**.

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

The next experiments should introduce controlled variation in recipient/context and then consequences of communicative actions.

The progression is:

```text
fixed state + objective
        ↓
controlled act selection                [current]
        ↓
recipient/context variation             [next]
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

A future learned policy should therefore be judged by its ability to change appropriately after experience and transfer that change beyond the exact interaction from which it was learned.

---

## 7. Provenance rule for future work

Every future communication milestone should preserve:

1. the observation that motivated the hypothesis;
2. the hypothesis as it existed before the result;
3. the controlled experiment;
4. the exact CI/reproduction result that matters;
5. failures as well as successes;
6. what the result does and does not establish;
7. the hypothesis changed by the result; and
8. why the next experiment follows from the evidence.

This history is part of Cognitia's research evidence, not merely project documentation.
