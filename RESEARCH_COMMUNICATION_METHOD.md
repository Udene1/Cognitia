# Communication Research Method

## Status

**Active methodological constraint and provenance record.**

Cognitia's communication capability is being investigated as a cognitive capability, not as a language-generation problem.

For the foreseeable research horizon, Cognitia must **not depend on an LLM** for cognition, communicative-act selection, epistemic control, learning, or experiment evaluation.

This is a research-method decision, not a claim that an LLM could never be useful for any future surface. If the constraint is ever changed, that change must itself be documented and experimentally justified.

## Why this constraint exists

An LLM can produce a fluent answer before we know whether Cognitia has learned:

- what it knows;
- what it does not know;
- what the interaction is trying to accomplish;
- which communicative action is appropriate;
- how much epistemic commitment is warranted; and
- whether the communication preserved the underlying cognitive state.

If an LLM performs those decisions for Cognitia, the experiment cannot establish that Cognitia learned them.

Therefore the early communication experiments must expose the decision process directly.

## Current research path

The communication problem emerged from examining Cognitia's earlier answer behavior. The observed weakness was not treated as a request for better prose. It raised a deeper hypothesis: Cognitia may possess useful problem-solving and epistemic structure but lack a sufficiently explicit capability for deciding **how to act communicatively on that internal state**.

That led to the research progression:

```text
answer behavior observed
        ↓
communication identified as a separate capability
        ↓
communicative cognition research hypothesis
        ↓
controlled communicative-act experiment
        ↓
deterministic implementation
        ↓
measured observations
        ↓
revised hypothesis / next experiment
```

The repository's research documents are part of the evidence trail. We should preserve the reasoning that caused each architectural change instead of only recording the final design.

## What the first experiment must prove

Experiment 1 holds the cognitive state fixed and varies the communicative objective.

The first implementation therefore selects from explicit communicative acts without producing natural-language prose.

A successful result would show that:

```text
same cognitive state
+ different objective
        ↓
different warranted communicative act
```

while:

```text
communicative act
        ↓
does not increase epistemic warrant
```

This separates:

```text
WHAT I KNOW
WHAT I WANT TO ACCOMPLISH
WHAT ACTION IS WARRANTED
HOW THE ACTION IS REPRESENTED
```

## No-LLM invariant

No experiment in this research path should use an LLM to:

- choose the communicative act;
- assign epistemic status;
- decide whether a claim is established;
- evaluate whether the experiment succeeded;
- manufacture training labels from surface answers; or
- silently repair a failed communicative decision.

Deterministic mechanisms, explicit rules, executable experiments, recorded observations, and later learned policies are preferred because they leave an inspectable causal trail.

This does **not** require Cognitia to remain rule-based forever. A future learning mechanism can replace an explicit mechanism only after experiments establish what was learned and the replacement can be independently evaluated.

## Evidence discipline

Every meaningful step should leave evidence in one or more of:

- research documents explaining the hypothesis and why it changed;
- executable experiment fixtures;
- automated tests and failure cases;
- structured communicative decisions;
- provenance linking decisions to cognitive state and evidence;
- durable observations and experiences;
- candidate models or policies;
- validation results.

A passing test establishes only the behavior that test actually measures. It is not evidence of general communication ability.

## Development rule

Do not build a large communication framework because the architecture sounds plausible.

Instead:

```text
hypothesis
→ smallest discriminating experiment
→ observation
→ failure analysis
→ revised hypothesis
→ next experiment
→ candidate abstraction
→ independent reproduction
→ transfer test
→ validation
→ integration
```

The research record should make it possible for another builder to understand not only **what Cognitia became**, but **why we believed each step was justified at the time**.

## Current boundary

The present implementation is deliberately small. It is evidence for a narrow question: whether objective changes can alter communicative-act selection while preserving epistemic status.

It is **not yet evidence** that Cognitia can:

- learn communication from interaction;
- model arbitrary audiences;
- compose long coherent messages;
- communicate naturally in unrestricted language;
- generalize communication policies broadly; or
- solve the full problem of communicative cognition.

Those require subsequent experiments.
