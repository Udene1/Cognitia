# Cognitia Discovery Research Agenda

Cognitia is not being designed as an LLM, an LLM wrapper, or a conventional agent framework. We do not assume that the eventual cognitive architecture needs a name yet. We are investigating what mechanisms are required for a machine to reason, investigate, learn, and potentially discover knowledge beyond what it was explicitly given.

## Core research question

> Can an artificial cognitive system investigate problems beyond the immediate capabilities of any individual model, construct genuinely novel hypotheses, test them, learn from failure, and progressively convert surviving hypotheses into reproducible knowledge?

## What "novel" means here

Novelty is not a measure of how many existing concepts were recombined. A recombination may be useful, but it is not sufficient evidence of discovery.

For Cognitia, discovery research is interested in hypotheses or explanatory structures that are not already represented in the system's current knowledge and that introduce a genuinely new explanatory or predictive claim.

A generated idea is not a discovery merely because it is unfamiliar to Cognitia. It must survive increasingly strong evidence.

## Discovery epistemic ladder

```text
candidate idea
    ↓
novel relative to current knowledge
    ↓
plausible / internally coherent
    ↓
falsifiable prediction
    ↓
controlled test or simulation
    ↓
internal evidence
    ↓
independent reproduction
    ↓
external validation
    ↓
accepted scientific knowledge
```

Cognitia must never collapse these states into a single confidence number.

## Unknown-space exploration

The target is not simply to search harder for known answers.

Cognitia should eventually be able to recognize:

1. what its current models explain;
2. what observations remain unexplained;
3. which assumptions constrain its current hypothesis space;
4. where alternative representations may be required;
5. which plausible hypotheses are absent from its current knowledge;
6. what observations would distinguish competing hypotheses;
7. which experiment, calculation, simulation, or information acquisition would most reduce uncertainty.

The difficult research problem is therefore **hypothesis-space expansion**, not random idea generation.

## Discovery loop

```text
observe
  ↓
model current knowledge
  ↓
identify anomaly / explanatory gap
  ↓
construct candidate hypothesis space
  ↓
explore alternatives
  ↓
derive predictions
  ↓
select discriminating test
  ↓
experiment / simulate / acquire evidence
  ↓
observe outcome
  ↓
revise beliefs and representations
  ↓
retain, challenge, revise, or reject
  ↓
formalize surviving result
```

## Research experiments

### D1 — Anomaly recognition

Can Cognitia distinguish an ordinary unknown from an observation that conflicts with its current explanatory models?

### D2 — Hypothesis-space expansion

When existing explanations fail, can Cognitia construct alternatives that are not simply retrieved from existing knowledge?

### D3 — Novel prediction

Can a newly generated hypothesis produce a prediction that was not explicitly supplied as an observation?

### D4 — Discriminating experiment selection

Can Cognitia choose an experiment because it separates competing hypotheses rather than merely because it is easy to perform?

### D5 — Discovery under capability limits

When Cognitia cannot perform the ideal experiment, can it construct a qualified approximation, state the epistemic limitation, and identify the verification path?

### D6 — Failed-discovery learning

Can Cognitia learn from a failed hypothesis without simply memorizing that the exact hypothesis was wrong?

### D7 — Independent reproduction

Can an independently implemented verifier reproduce a Cognitia-generated result without relying on Cognitia's internal reasoning trace as proof?

## Completed foundation milestones

### Discovery gap representation

Cognitia now has an explicit workspace for observations, explanation assessments, explanatory gaps, and hypothesis candidates. Contradicted or unexplained observations become investigation targets without automatically generating an answer. This preserves the distinction between an anomaly and a solution.

### Bounded hypothesis-space construction

Cognitia can now construct a traceable alternative space from an explicit explanatory model. The initial transformations are:

- relax an assumption;
- reverse an assumption;
- partition by an existing context variable;
- introduce an explicitly identified missing variable.

Each alternative retains its source model, transformation, changed element, epistemic status, and unassessed novelty status. This is deliberately a **search primitive**, not a claim of autonomous scientific creativity.

### Falsifiable prediction contracts

A hypothesis can now be paired with a condition, expected outcome, and explicit falsifier. Cognitia does not infer that a prose proposition is scientifically testable merely because it sounds plausible.

### Discriminating experiment selection

Cognitia can select a test when competing hypotheses make different predictions under the same condition. A test is therefore selected for its discriminatory value, not merely because a test exists.

### CI research experiment

The discovery CI experiment constructs multiple alternatives from a baseline model, creates two competing hypotheses, derives conflicting predictions, and selects a discriminating experiment. The experiment explicitly reports that it has made **no novelty claim**.

## Current architectural consequence

The existing knowledge, memory, hypothesis, verification, capability, failure-analysis, candidate, and durable-state systems are foundations for discovery. The discovery layers must remain connected to those systems rather than becoming a separate idea-generation subsystem.

In particular, durable cognitive state must be replayable into active cognition. A remembered hypothesis or capability outcome is useful only when a fresh process can reconstruct the state and use it in a subsequent decision.

## Next research attack

The next difficult step is not adding more hand-written transformations. We need to investigate whether Cognitia can learn **which transformations are useful** from failed and successful investigations, while preserving provenance and avoiding a growing list of domain-specific rules.

That means moving toward a representation in which assumptions, variables, dependencies, constraints, predictions, and outcomes are first-class objects. The search mechanism should then operate over that representation and be evaluated by transfer and held-out evidence.

The progression is:

```text
explicit model
→ explanatory gap
→ alternative hypothesis space
→ prediction
→ discriminating experiment
→ observed result
→ hypothesis revision
→ learned search strategy
```

The key research question is whether the final arrow can become learned cognition rather than a collection of manually encoded heuristics.

## Non-goals

- Do not call an LLM to supply Cognitia's intelligence.
- Do not equate novelty with random recombination.
- Do not call an internally generated hypothesis a scientific law.
- Do not treat persistence as evidence of truth.
- Do not treat a successful single experiment as universal proof.
- Do not optimize for impressive-looking generated papers before the underlying discovery process is defensible.

## Long-term objective

The strongest future demonstration would be a problem for which the relevant answer is absent from Cognitia's starting knowledge, followed by a complete trace showing:

```text
unexplained observation
→ novel hypothesis
→ novel prediction
→ discriminating experiment
→ result
→ belief revision
→ independent reproduction
```

Only then should Cognitia claim that it has demonstrated a meaningful form of machine discovery.
