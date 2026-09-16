# Communication Research History

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

The implementation introduces `CommunicationProjection` and explicit representations including `STRUCTURED`, `CONCISE`, and `EXPLANATORY`.

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

### CI result — 2026-09-16

PR #10 (`Experiment 3: representation-preserving communication`) was exercised by workflow run **35058802223**. The ordinary `test` job collected **197 tests** and finished with **196 passed, 1 failed, 1 warning**.

The failure is a **communication-research failure**, not a syntax/build/infrastructure failure. The failing test was:

```text
test_surface_representations_preserve_the_same_communication_contract
```

The test selected `REPORT_CURRENT_STATE` for an unresolved state and projected the same decision into `STRUCTURED`, `CONCISE`, and `EXPLANATORY` representations. The projection contract required each representation to preserve the same selected act, claims, evidence, uncertainty, and verification requirement.

The observed concise projection payload was:

```text
act:report_current_state
claims:H1
uncertainty:no root cause is established;H1 and H2 remain discriminable candidates
verification:required
```

It omitted:

```text
evidence:E1
```

The assertion therefore failed on the concrete observation:

```text
AssertionError: assert 'evidence:E1' in (...)
```

This is behaviorally meaningful because the representation surface changed the observable communication contract: the underlying decision contained evidence identity `E1`, but the concise representation did not expose it. The preservation checker did not silently repair the projection; CI exposed the loss.

The cognitive-transfer job in the same workflow completed successfully across the existing durable-state, transfer, discovery, evidence, language, and answer-construction stages. Therefore this result does **not** show that Cognitia's broader cognitive-transfer system failed. It isolates the observed failure to Experiment 3's communication representation layer.

### Research interpretation

Experiment 3 currently **fails its preservation hypothesis** for the tested concise representation.

The result does not establish that concise communication is impossible. It establishes that the current concise projection implementation cannot be considered representation-preserving under the contract we defined. In particular, shortening the payload currently removes evidence identity even though evidence is part of the contract that the experiment explicitly requires to survive representation changes.

This failure must remain visible as research evidence until the hypothesis is revised and a subsequent experiment demonstrates what actually changes. The failing test should not be weakened merely to make CI green.

### Evidence boundary

The result is narrow. It demonstrates one concrete semantic-loss mode in one explicit representation pipeline. It does not establish general natural-language communication failure, learned communication failure, or failure of the broader cognitive architecture.

### Next research question

Before repairing the implementation blindly, determine whether the preservation contract is correctly defined for all three representation classes. If evidence identity is a required commitment across surfaces, the next implementation hypothesis is that every representation must retain a machine-observable evidence reference even when its human-facing organization is concise. A subsequent CI run must then test whether that revised hypothesis preserves the contract without silently dropping or inventing evidence.

---

## 6. Experiment 3A: preservation boundary

Experiment 3A was derived directly from the Experiment 3 failure rather than from a desire to make the failing test green.

The competing hypotheses are:

- **H3A-direct:** every communication surface must directly expose evidence identity;
- **H3A-recoverable:** evidence may be compressed out of the top-level payload when the same surface contains a deterministic, machine-observable reference from which the exact evidence identity can be recovered;
- **H3A-lossy:** evidence may be silently omitted as long as claims and uncertainty remain unchanged.

The implementation now adds `COMPACT_REFERENCED` and `assert_observable_evidence_recovery`.

The controlled tests hold the cognitive state, recipient, objective, selected act, claims, epistemic status, evidence identity, uncertainty, and verification requirement constant while varying only evidence encoding. The new boundary tests therefore distinguish direct evidence, explicitly referenced evidence, and the existing silent-omission negative control.

Importantly, the original `CONCISE` behavior remains unchanged. It is not repaired in place. It continues to omit `evidence:E1`, and the new preservation invariant explicitly rejects it because no recovery reference exists.

At this point the implementation establishes a **candidate experimental boundary**, not a validated research result. The next CI execution is the observation needed to determine whether lossless reference is sufficient or whether evidence must remain directly visible on every surface.

---

## 7. Observation during communication research: Cognitia constructed an English synthesis surface

While inspecting the broader CI run, the Roman Empire research synthesis produced a complete English-language answer in the CI output. This was recorded as an observation during the communication experiment, not as evidence that the communication problem had already been solved.

The exact path was inspected on the CI checkout:

1. `tests/ci/research_synthesis.py` runs `OpenEndedResearch().investigate(...)`, passes the acquired result into `ResearchSynthesisEngine().synthesize(result)`, and prints `synthesis.render()`. The benchmark itself contains no hand-authored Roman Empire factors; the evidence landscape is acquired and extracted by Cognitia. 
2. `DocumentClaimExtractor` deterministically splits acquired documents into candidate sentences and retains each as an `ExtractedClaim` with source observation, proposition, confidence, uncertainty, attribution, polarity, and other metadata. It explicitly states that it extracts claims without an LLM and does not promote them to truth.
3. `ResearchSynthesisEngine` deterministically factorizes causal claims using regular-expression patterns, classifies domains from keyword scores, constructs a cautious thesis, identifies contrary claims, generates distinguishing evidence, caveats, and next actions, and then `ResearchSynthesis.render()` assembles those structured fields into the English output.

The observed English answer therefore was **constructed by Cognitia's deterministic synthesis/rendering path**, rather than written by the assistant after the CI run. The source-derived contribution sentences are carried from extracted claims, while the connective thesis, headings, caveats, and next-action language are generated by the synthesis engine's deterministic templates.

This distinction matters. The observation demonstrates that Cognitia can currently transform a structured evidence/synthesis state into a coherent English communication surface without an LLM performing the rendering. It does **not** yet demonstrate learned natural-language communication, general language understanding, or representation-independent communication. It is evidence that an existing cognitive/evidence pipeline already has a nontrivial deterministic communication surface that our communication research can now interrogate.

### Research consequence

The observation strengthens the reason for continuing the communication route: Cognitia already has an English surface produced from internal structured state, so we can test whether that surface preserves the same communicative contract as the underlying state, whether alternative surfaces can express the same act without semantic loss, and whether interaction consequences can later influence act selection.

The English synthesis observation is therefore preserved as part of the historical evidence trail rather than treated as a completed milestone.

---

## 8. Provenance rule

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
