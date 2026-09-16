# Milestone: Recipient/Context-Conditioned Communication

## Status

**Experiment 2 implementation validated by CI.**

## Research question

Given the same underlying cognitive state and communicative objective, can Cognitia select different communicative actions as controlled recipient context changes while preserving epistemic commitments?

## Why this experiment follows Experiment 1

Experiment 1 showed objective-dependent act selection. It did not establish that communication is genuinely interaction-conditioned because the recipient was held constant.

Experiment 2 therefore varies recipient role while keeping the state and objective fixed. This is the smallest next experiment that can discriminate between:

```text
communication = objective lookup
```

and

```text
communication = action selection conditioned by cognitive + interaction state
```

## Controlled result

For the unresolved controlled state and objective `INFORM`, CI observed:

```text
OPERATOR
    → REPORT_CURRENT_STATE

DECISION_MAKER
    → SUPPORT_DECISION_UNDER_UNCERTAINTY

LEARNER
    → EXPLAIN_UNCERTAINTY
```

The same unresolved uncertainty and verification requirement remained present across the decisions.

## CI evidence

PR #9: `Experiment 2: recipient-context-conditioned communication`

GitHub Actions run: **35058177100**

The `test` job collected **195 tests** and completed with:

```text
195 passed, 1 warning in 0.97s
```

The communication test module contained **8 tests**, all passed. The warning was an existing `PytestCollectionWarning` for `TestResult` and did not fail the run.

The `cognitive-transfer` job also completed successfully. It restored prior cognitive state, continued through transfer, persistence, discovery, evidence reasoning, language, and answer-construction stages, and uploaded the answer-core diagnostics artifact successfully.

## What Cognitia did

The important observation is behavioral rather than merely CI status. With the cognitive state and `INFORM` objective held constant, changing only the explicit recipient role changed the selected communicative action.

The decision record retained the recipient role, state identity, uncertainty, and verification requirement. Epistemic-preservation checks continued to reject unsupported upgrades.

This supports the narrower proposition that the current communication layer can condition communicative action selection on an explicit interaction-context variable.

## Interpretation

This is not evidence of a learned recipient model. The recipient-role mapping is explicitly implemented and exists to expose the capability for controlled research.

The result does not establish general audience adaptation, arbitrary context handling, natural-language adaptation, or consequence-based communication learning.

## Evidence boundary

Established by this milestone:

- recipient context can be represented separately from cognitive state;
- recipient context can influence communicative-act selection in the tested cases;
- epistemic commitments can remain preserved while that selection changes;
- the communication layer coexists with the existing cognitive-transfer path.

Not established:

- learned recipient modeling;
- general audience adaptation;
- open-ended context sensitivity;
- natural-language surface adaptation;
- communication consequence learning.

## Next experiment

Hold the selected communicative act fixed and vary the representation/surface used to express it.

Test whether different representations preserve:

- the communicative act;
- claim identity;
- evidence identity;
- uncertainty;
- epistemic status;
- verification requirements.

Only after representation preservation is experimentally exposed should communication consequences become the learning signal.
